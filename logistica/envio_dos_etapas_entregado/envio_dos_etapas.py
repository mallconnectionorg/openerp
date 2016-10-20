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
from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID

class stock_picking(osv.osv):
    _inherit = "stock.picking"


    def check_stock_salida_destino(self, cr, uid, ids):
        warehouse_obj = self.pool.get('stock.warehouse')
        res = False
        destino_stock = False
        destino_salida = False
        pick = self.browse(cr, SUPERUSER_ID, ids[0])
        location_dest_id = False
        stock_salida = True
        for move in pick.move_lines:
            if not location_dest_id:
                location_dest_id = move.location_dest_id.id
            else:
                if move.location_dest_id.id != location_dest_id:
                    stock_salida = False
        warehouse_stock_ids = warehouse_obj.search(cr, SUPERUSER_ID, [('lot_stock_id','=',location_dest_id)])
        warehouse_salida_ids = warehouse_obj.search(cr, SUPERUSER_ID, [('lot_output_id','=',location_dest_id)])
        if (warehouse_stock_ids or  warehouse_salida_ids) and stock_salida:
            self.write(cr, uid, ids, {'entregado': True})
            res = True
        return res

    def entregado_met(self, cr, uid, ids, context=None):
        if len(ids) > 1:
            return True
        css_destino = self.check_stock_salida_destino(cr, uid, ids)
        if css_destino:
            res = True
        else:
            res = super(stock_picking, self).entregado_met(cr, uid, ids, context=None)
        return res

