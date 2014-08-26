# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Hugo Santos <hugo.santos@factolibre.com>
#    Copyright 2014 Factor Libre S.L
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import boto
import urlparse
import base64
import logging
import hashlib
from openerp.osv import orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class DocumentAmazonS3(orm.Model):
    _inherit = 'ir.attachment'

    def _s3_connection_and_bucket(self, location):
        loc_parse = urlparse.urlparse(location)
        assert loc_parse.scheme == 'amazons3', \
            "This method is intended only for amazons3://"

        access_key_id = loc_parse.username
        secret_key = loc_parse.password

        if not access_key_id or not secret_key:
            raise orm.except_orm(
                _('Error'),
                _('Must define access_key_id and secret_access_key '
                  'in amazons3:// scheme')
            )

        s3_conn = boto.connect_s3(access_key_id, secret_key)
        s3_bucket = s3_conn.lookup(loc_parse.hostname)
        if not s3_bucket:
            #Try to create Bucket
            s3_bucket = s3_conn.create_bucket(loc_parse.hostname)

        return s3_bucket

    def _file_read(self, cr, uid, location, fname, bin_size=False):
        loc_parse = urlparse.urlparse(location)
        if loc_parse.scheme == 'amazons3':
            s3_bucket = self._s3_connection_and_bucket(location)
            s3_key = s3_bucket.get_key(fname)
            if not s3_key:
                return False

            if bin_size:
                read = s3_key.size
            else:
                read = base64.b64encode(s3_key.get_contents_as_string())
        else:
            read = super(DocumentAmazonS3, self)._file_read(
                cr, uid, location, fname, bin_size=bin_size)
        return read

    def _file_write(self, cr, uid, location, value):
        loc_parse = urlparse.urlparse(location)
        if loc_parse.scheme == 'amazons3':
            s3_bucket = self._s3_connection_and_bucket(location)
            bin_value = value.decode('base64')
            fname = hashlib.sha1(bin_value).hexdigest()

            s3_key = s3_bucket.get_key(fname)
            if not s3_key:
                s3_key = s3_bucket.new_key(fname)

            s3_key.set_contents_from_string(bin_value)
        else:
            fname = super(DocumentAmazonS3, self)._file_write(
                cr, uid, location, value)

        return fname

    def _file_delete(self, cr, uid, location, fname):
        loc_parse = urlparse.urlparse(location)
        if loc_parse.scheme == 'amazons3':
            count = self.search(cr, SUPERUSER_ID, [
                ('store_fname', '=', fname)
            ], count=True)
            if count <= 1:
                s3_bucket = self._s3_connection_and_bucket(location)
                s3_key = s3_bucket.get_key(fname)
                if not s3_key:
                    return False
                try:
                    s3_key.delete()
                except Exception, e:
                    _logger.error("_file_delete could not unlink %s"
                                  " from S3. Error: %s") % (fname, e.message)
        else:
            return super(DocumentAmazonS3, self)._file_delete(
                cr, uid, location, fname)

    def get_s3_url(self, cr, uid, att_id, expires_in=600, context=None):
        if context is None:
            context = {}

        att = self.browse(cr, uid, att_id, context=context)
        url = False
        location = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'ir_attachment.location')
        if location:
            loc_parse = urlparse.urlparse(location)

            assert loc_parse.scheme == 'amazons3', \
                "This method is intended only for amazons3://"

            if att.store_fname:
                s3_bucket = self._s3_connection_and_bucket(location)
                s3_key = s3_bucket.get_key(att.store_fname)
                if s3_key:
                    url = s3_key.generate_url(expires_in)

        return url
