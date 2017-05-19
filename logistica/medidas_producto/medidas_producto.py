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
from openerp.osv import fields, osv

class product_product(osv.osv):
    _inherit = "product.product"

    def _get_volumen_producto(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict()
        for producto in self.browse(cr, uid, ids):
            if producto.ancho and producto.alto and producto.largo:
                res[producto.id] = (producto.ancho * producto.alto * producto.largo) / 1000
            else:
                res[producto.id] = 0.0
        return res

    _columns = {
        'largo': fields.float('Largo (cm.)'),
        'ancho': fields.float('Ancho (cm.)'),
        'alto': fields.float('Alto (cm.)'),
        'volumen': fields.function(_get_volumen_producto, type='float', string='Volumen (lts.)', store=True),
    }
