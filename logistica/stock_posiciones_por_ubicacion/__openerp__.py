# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'PosicionesPorUbicacion',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """
Este modulo implementa la posibilidad de manejar multiples posiciones por ubicacion. Por ejemplo,
puede dividir una ubicacion entre distintas posiciones entre racks y estantes. Además puede establecer
un flujo de reabastecimiento entre las posiciones.
    """,
    'author': 'Cesar Lopez Aguillon',
    'depends': ['stock','point_of_sale'],
    'data': [
        'stock_posiciones_por_ubicacion.xml',
        'stock_posiciones_por_ubicacion_data.xml',
        'wizard/stock_posiciones_por_ubicacion_wizard.xml',
        'security/ir.model.access.csv',
        'security/stock_posiciones_por_ubicacion_security.xml',
    ],
    'demo': [],
    'installable': True,
    'test': [],
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
