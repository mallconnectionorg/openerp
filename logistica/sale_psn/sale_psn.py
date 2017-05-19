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
from osv import fields, osv

#----------------------------------------------------------
# Sale PSN Wizard
#----------------------------------------------------------
class sale_psn_wizard(osv.osv_memory):
    _name = "sale.psn.wizard"

    def _get_sale_psn(self, cr, uid, active_id, context=None):
        res = []
        sol_obj = self.pool.get('sale.order.line')
        sol = sol_obj.browse(cr, uid, active_id)
        for sn in sol.psn_ids:
            res.append(self.pool.get('sale.product.serial.number').create(cr, uid, {'name':sn.name,'psn_id':sn.id}))
        return res

    def _get_sol_state(self, cr, uid, active_id, context=None):
        sol_obj = self.pool.get('sale.order.line')
        sol = sol_obj.browse(cr, uid, active_id)
        res = sol.state
        return res

    _columns = {
        'spsn_ids': fields.one2many('sale.product.serial.number','spw_id', 'Numeros de Serie', readonly=True, states={'draft':[('readonly',False)]}),
        'sol_id': fields.many2one('sale.order.line','Sale Line'),
        'state': fields.char('Estado', size=24, readonly=True),
    }

    _defaults = {
        'sol_id': lambda self, cr, uid, c: c.get('active_id', False),
        'spsn_ids': lambda self, cr, uid, c: self._get_sale_psn(cr, uid, c.get('active_id', False), context=c),
        'state': lambda self, cr, uid, c: self._get_sol_state(cr, uid, c.get('active_id', False), context=c),
    }

    def guardar_cambios(self, cr, uid, ids, context=None):
        so_obj = self.pool.get('sale.order')
        psn_obj = self.pool.get('product.serial.number')
        sol_obj = self.pool.get('sale.order.line')
        for spw in self.browse(cr, uid, ids, context=context):
            product_id = spw.sol_id.product_id and spw.sol_id.product_id.id or False
            if product_id:
                if not spw.sol_id.product_id.psn:
                    return {'type': 'ir.actions.act_window_close'}

            spsn_ids_list = []
            psn_ids = []
            for spsn in spw.spsn_ids:
                spsn_ids_list.append(spsn.id)
                if spsn.psn_id:
                    if spsn.psn_id.id not in psn_ids:
                        psn_ids.append(spsn.psn_id.id)
                else:
                    if product_id:
                        psn_search_ids = psn_obj.search(cr, uid, [('name','=',spsn.name),('product_id','=',product_id)])
                    if len(psn_search_ids) == 1:
                        if psn_search_ids[0] not in psn_ids:
                            psn_ids.append(psn_search_ids[0])
            cantidad = len(psn_ids)
            if spw.sol_id and psn_ids:
                self.pool.get('sale.order.line').chequea_psn(cr, uid, spw.sol_id, psn_ids)
                psn_obj.write(cr, uid, psn_ids, {'sale_line_id': spw.sol_id.id})
                sol_obj.write(cr, uid, [spw.sol_id.id], {'product_uom_qty':float(cantidad)})
                psn_sale_line_id_ids = psn_obj.search(cr, uid, [('sale_line_id','=',spw.sol_id.id)])
                for psnid in psn_sale_line_id_ids:
                    if psnid not in psn_ids:
                        psn_obj.write(cr, uid, [psnid], {'sale_line_id': False})
            self.pool.get('sale.product.serial.number').unlink(cr, uid, spsn_ids_list)

        return {'type': 'ir.actions.act_window_close'}

#----------------------------------------------------------
# Sale Product Serial Numbers
#----------------------------------------------------------
class sale_product_serial_number(osv.osv_memory):
    _name = "sale.product.serial.number"

    _columns = {
        'name': fields.char('Numero de Serie', size=64),
        'spw_id': fields.many2one('sale.psn.wizard','Sale PSN Wizard'),
        'psn_id': fields.many2one('product.serial.number','PSN'),
    }

#----------------------------------------------------------
# Product Serial Number
#----------------------------------------------------------
class product_serial_number(osv.Model):
    _inherit = 'product.serial.number'

    _columns = { 
        'sale_line_id': fields.many2one('sale.order.line', 'Linea de Orden de Venta', ondelete='set null', select=True, readonly=True),
    }

#----------------------------------------------------------
# Sale Order Line
#----------------------------------------------------------
class sale_order_line(osv.Model):
    _inherit = 'sale.order.line'

    _columns = { 
        'psn_ids': fields.one2many('product.serial.number', 'sale_line_id', 'Numeros de Serie', readonly=True),
    }

    def chequea_psn(self, cr, uid, sol, psn_ids):
        if not psn_ids:
            raise osv.except_osv('Error','No ha ingresado numeros de serie.\nProducto %s.'%(sol.product_id.default_code))
            return False
        ubicacion_origen_tienda = sol.order_id.shop_id.warehouse_id.lot_stock_id.id
        res = True
        psn_obj = self.pool.get('product.serial.number')
        origen_psn = False
        mismo_origen = True
        for psn in psn_obj.browse(cr, uid, psn_ids):
            if not origen_psn:
                origen_psn = psn.location_id.id
            else:
                if origen_psn != psn.location_id.id:
                    mismo_origen = False
        if not mismo_origen:
            raise osv.except_osv('Error','Los numeros de serie utilizados no comparten la misma ubicacion de origen.')
            return False
        if not origen_psn:
            raise osv.except_osv('Error','Los numeros de serie utilizados no tienen ubicacion de origen.')
            return False
        if ubicacion_origen_tienda != origen_psn:
            raise osv.except_osv('Error','Los numeros de serie utilizados no estan en esta bodega.')
            return False
        return res

    def asocia_psn_sale_line_stock_move_line(self, cr, uid, ids):
        move_obj=self.pool.get('stock.move')
        for line in self.browse(cr, uid, ids):

            if not line.product_id.psn:
                return True

            lista_psn = []
            for psn in line.psn_ids:
                lista_psn.append(psn.id)

            self.chequea_psn(cr, uid, line, lista_psn)

            if len(line.move_ids) > 1:
                lista_stock_move = []
                for move in line.move_ids:
                    if move.state != 'cancel':
                        if (move.product_qty == line.product_uom_qty) and (len(lista_psn) == line.product_uom_qty):
                            lista_stock_move.append(move.id)
                if len(lista_stock_move) > 1:
                    raise osv.except_osv('Error','Tiene mas de un movimiento de stock para este producto %s y esta orden de venta. (%s movimientos)'%(line.product_id.default_code,str(len(lista_stock_move))))
                    return False
                elif len(lista_stock_move) == 1:
                    move_obj.write(cr, uid, [lista_stock_move[0]], {'product_serial_number_ids': [(6, lista_stock_move[0], lista_psn)]})
                else:
                    raise osv.except_osv('Error','No tiene movimientos de stock activos para este producto %s'%(line.product_id.default_code))
                    return False
            else:
                if len(line.move_ids) == 1:
                    move_obj.write(cr, uid, [line.move_ids[0].id], {'product_serial_number_ids': [(6, line.move_ids[0].id, lista_psn)]})
                else:
                    raise osv.except_osv('Error','No tiene movimientos de stock para este producto %s'%(line.product_id.default_code))
                    return False

        return True

#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class sale_order(osv.Model):
    _inherit = 'sale.order'

    def verifica_cantidad_series(self, cr, uid, order):
        for line in order.order_line:
            if line.product_id.psn:
                if line.product_uom_qty != len(line.psn_ids):
                    raise osv.except_osv('Error','Tiene una diferencia entre la cantidad de numeros de serie y \nla cantidad del siguiente producto %s'%(line.product_id.default_code))
                    return False
            else:
                if len(line.psn_ids) != 0:
                    raise osv.except_osv('Error','No puede usar numeros de serie para el siguiente producto %s'%(line.product_id.default_code))
                    return False
        return True

    def action_ship_create(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            line_ids = []
            for line in order.order_line:
                line_ids.append(line.id)
            self.pool.get('sale.order.line').asocia_psn_sale_line_stock_move_line(cr, uid, line_ids)
            self.verifica_cantidad_series(cr, uid, order)
            line_ids = []
        return res

