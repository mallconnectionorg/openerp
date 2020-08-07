#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Asientos adicionales
#   Copyright (C) 2020 Cesar Lopez Aguillon Mall Connection
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
    'name': "Asientos adicionales",
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': u"""
Este módulo permite crear asientos adicionales para un documento 
tributario.
""",
    'author': 'César López Aguillón',
    'website': 'https://www.mallconnection.org',
    "depends" : [
        "base",
        "account",
        "web",
    ],
    "update_xml" : [
        'asientos_adicionales_view.xml',
    ],
    "data" : [
        'security/ir.model.access.csv',
        'data/secuencia_asientos_adicionales.xml',
    ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
