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
    'name': 'TrazaEnvios',
    'version': '0.1',
    'category': 'Warehouse',
    'description': """Permite establecer numeros de seguimiento para los
        albaranes/bulto y las consolidaciones de bultos.""",
    'author': 'Cesar Lopez',
    'website': 'http://www.mallconnection.org',
    'depends': [
        'envio_dos_etapas',
        'point_of_sale',
        'sale',
        'stock',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'traza_envios.xml',
        'wizard/traza_envios_wizard.xml',
        'traza_secuencias.xml',
        'security/ot_security.xml',
        'traza_envios_report.xml',
        'sale_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
}
