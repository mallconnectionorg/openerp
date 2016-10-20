# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP S.A. (<http://www.openerp.com>).
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
    'name': 'Instituciones Financieras Chile',
    'version': '1.0',
    'category': 'Localization/Chile',
    "description": """
    
    Fichas de Bancos y Cooperativas, establecidos por SBIF
    
        - Bancos Establecidos en Chile
        - Cooperativas de Ahorro y Crédito
        - Bancos Estatales
        - Sucursales de Bancos Extranjeros
    
    """,
    'author': 'Iván Masías - ivan.masias.ortiz@gmail.com, Rev. Pedro Arroyo<parroyo@mallconnection.com>',
    'website': '',
    'depends': [ 'base'],
    'data': [
	'data/res.bank.csv',
	'view/res_bank.xml'
    ],
    'installable': True,
    'active': False,
}
