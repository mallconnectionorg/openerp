#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   DTE Chile OpenERP 7
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
        'name' : 'DTE Chile OpenERP 7',
        'version' : '0.1',
        'author' : u'César López Aguillón',
        'website' : 'www.mallconnection.org',
        'category' : 'Accounting & Finance',
        'description': u"""Este módulo permite consumir servicios de un
servidor de LibreDTE y generar documentos tributarios electrónicos
(33, 34, 56, 61) que están de acuerdo a la normativa del servicio de
impuestos internos de Chile desde un servidor de OpenERP 7. En si, este
módulo sólo hace uso de la API REST y el SDK que están disponibles a
través del mismo proyecto LibreDTE (http://libredte.github.io/
https://github.com/LibreDTE). Deben estar instalados los módulos request
y bs4 para python 2.7 (python-requests python-bs4). Requiere además la 
versión de report_webkit disponible en https://github.com/mallconnectionorg/openerp""",
        'depends' : [
            'base',
            'account',
            'edi',
            'mail',
            'sale',
            'report_webkit',
            ],
        'init_xml' : [],
        'demo_xml' : [],
        'update_xml' : [
            'views/mc_dte_base_view.xml',
            'views/account_view.xml',
            'views/res_partner_view.xml',
        ],
        'data' : [
            'security/ir.model.access.csv',
            'data/data_reporte.xml',
            'data/report_factura_nota_mako.xml',
        ],
        'installable': True,
        'auto_install': False,
}
