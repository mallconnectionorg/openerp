#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Punto de Venta MC
#   Copyright (C) 2016 Cesar Lopez Aguillon Mall Connection
#   <http://www.mallconnection.org>.
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
    'name': 'Punto de Venta MC',
    'version': '0.1',
    'category': 'Point Of Sale',
    'description': """
Agrega el campo de tienda al usuario de sistema y un cajero al pedido de
venta. Además modifica la posición del vendedor en el formulario de
venta.
    """,
    'author': 'Cesar Lopez Aguillon',
    'website': 'http://www.mallconnection.org',
    'depends': ['point_of_sale',],
    'init_xml': [],
    'update_xml': ['res_users_view.xml','point_of_sale_view.xml'],
    'demo_xml': [],
    'test':[],
    'installable': True,
}
