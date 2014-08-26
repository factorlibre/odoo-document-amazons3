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

{
    'name': 'Document: Amazon S3',
    'version': '1.0',
    'category': 'Knowledge Management',
    'depends': ['document'],
    'external_dependencies': {
        'python': ['boto'],
    },
    'author': 'Factor Libre S.L',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'description': """
Amazon S3 Document Management
=================

Manages Document attachments with Amazon S3, using boto amazon library (https://github.com/boto/boto)

To use must define ir_attachment.location param as:

amazons3://access_key_id:secret_access_key@bucket

""",
    'images': [],
    'demo': [],
    'data': [],
    'installable': True,
    'application': False
}
