#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Cesar Lopez
#   Copyright (C) 2011 Mall Connection(<http://www.mallconnection.org>).
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
    'name': 'EnvioDosEtapas',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """Este modulo habilita el envio en dos etapas de cada albaran.
En la primera etapa se envia hacia la ubicación de entrada del destino y una vez
que se recibieron los productos, se presiona un botón que hace el movimiento desde
la ubicacion de entrada del destino hacia la ubicacion de stock del destino.""",
    'author': 'Cesar Lopez',
    'website': 'http://www.mallconnection.org',
    'depends': [
        'point_of_sale',
        'sale',
        'stock',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/envio_dos_etapas_wizard.xml',
        'envio_dos_etapas.xml',
    ],
    'demo_xml': [],
    'installable': True,
}
