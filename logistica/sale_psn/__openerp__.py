# -*- coding: utf-8 -*-
##############################################################################
#
#   Cesar Lopez
#   Copyright (C) 2011 Cesar Lopez(<http://www.mallconnection.org>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'SaleProductSerialNumber',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """Agrega un boton en sale.order.line para ingresar PSN (Product Serial Numbers).""",
    'author': 'Cesar Lopez Aguillon',
    'website': 'http://www.mallconnection.org',
    'depends': ['stock', 'sale', 'sale_stock', 'psn'],
    'init_xml': [],
    'update_xml': ['sale_psn_view.xml',],
    'demo_xml': [],
    'test':[],
    'installable': True,
}
