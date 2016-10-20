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
from openerp import SUPERUSER_ID
import time
import datetime
import logging

class lineas_ajuste_entrega(osv.osv_memory):
    _name = 'lineas.ajuste.entrega'
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', string="Producto", required=True),
        'quantity': fields.float("Cantidad", required=True),
        'ajuste_id': fields.many2one('ajuste.de.entrega', string="Ajuste"),
        'move_id': fields.many2one('stock.move', "Movimiento de stock"),
    }

lineas_ajuste_entrega()

class lineas_ajuste_entrega_movimientos(osv.osv_memory):
    _name = 'lineas.ajuste.entrega.movimiento'

    _columns = {
        'product_id': fields.many2one('product.product', "Producto"),
        'quantity': fields.float("Cantidad"),
        'ajuste_id': fields.many2one('ajuste.de.entrega', "Ajuste"),
        'origen': fields.char("Origen", size=32),
        'destino': fields.char('Destino', size=32),
        'albaran': fields.char("Albaran", size=32),
        'fecha': fields.datetime('Fecha'),
        'estado': fields.char("Estado", size=32),
    }

lineas_ajuste_entrega_movimientos()

class ajuste_de_entrega(osv.osv_memory):
    _name = 'ajuste.de.entrega'

    _columns = {
        'lineas_ajuste_ids': fields.one2many('lineas.ajuste.entrega','ajuste_id','Productos'),
        'tipo_ajuste': fields.selection([('sobrante', 'Productos sobrantes'), ('faltante', 'Productos faltantes'), ('ninguno', 'Ninguno')], 'Tipo de ajuste',required=True),
        'picking_id': fields.many2one('stock.picking','Albaran'),
        'movimientos_de_ajuste_ids': fields.one2many('lineas.ajuste.entrega.movimiento','ajuste_id','Movimientos de ajuste',)
    }

    _defaults = {
        'picking_id': lambda self, cr, uid, c: c.get('active_id', False),
    }

    def default_get(self, cr, uid, fields, context=None):
        result1 = []
        result2 = []
        if context is None:
            context = {}
        res = super(ajuste_de_entrega, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        if record_id:
            pick = pick_obj.browse(cr, uid, record_id, context=context)
        else:
            pick = False
        if pick:
            if pick.tipo_envio_mc == 'ajuste':
                raise osv.except_osv('Error','No se puede ajustar un albaran que ya es de ajuste, debe hacer uno nuevo si quiere corregir este docuemto.')
                return False
            res.update({'tipo_ajuste': 'ninguno'})
            albaranes_de_ajuste_ids = pick_obj.search(cr, uid, [('tipo_envio_mc','=','ajuste'),('backorder_id','=',pick.id)])
            move_ids = []
            for picking_ajuste in pick_obj.browse(cr, uid, albaranes_de_ajuste_ids):
                for move_ajuste in picking_ajuste.move_lines:
                    #Crear los movimientos de ajuste en memoria
                    valores_creacion = {
                        'product_id': move_ajuste.product_id.id,
                        'quantity': move_ajuste.product_qty,
                        'origen': move_ajuste.location_id.name,
                        'destino': move_ajuste.location_dest_id.name,
                        'albaran': move_ajuste.picking_id.name,
                        'fecha': move_ajuste.date,
                        'estado': move_ajuste.state,
                    }
                    result2.append(valores_creacion)
            res.update({'movimientos_de_ajuste_ids': result2})
            for line in pick.move_lines:
                result1.append({'product_id': line.product_id.id, 'quantity': line.product_qty,'move_id':line.id})
            res.update({'lineas_ajuste_ids': result1})
        return res

    def chequea_ubicacion_origen_destino(self, cr, uid, ids, picking, tipo_ajuste, stock_move=False, context=None):
        origen_id = False
        destino_id = False

        mismo_destino = True
        mismo_origen = True
        ubicacion_destino = False
        ubicacion_origen = False
        for move in picking.move_lines:

            if not ubicacion_destino:
                ubicacion_destino = move.location_dest_id.id
            else:
                if move.location_dest_id.id != ubicacion_destino:
                    mismo_destino = False

            if not ubicacion_origen:
                ubicacion_origen = move.location_id.id
            else:
                if move.location_id.id != ubicacion_origen:
                    mismo_origen = False

        if mismo_destino:
            destino = ubicacion_destino
        else:
            raise osv.except_osv('Error','No se puede obtener la ubicacion de destino')
            return False

        if mismo_origen:
            origen = ubicacion_origen
        else:
            raise osv.except_osv('Error','No se puede obtener la ubicacion de origen')
            return False

        #Verificar si la ubicacion de origen es del tipo entrada, si es
        #asi se debe hacer un by-pass y seleccionar la ubicacion de origen
        #de la backorder_id porque debio venir desde una tienda o bodega
        bodega = self.pool.get('stock.warehouse')
        warehouse_ids = bodega.search(cr, SUPERUSER_ID, [('lot_input_id','=',origen)])
        if warehouse_ids:
            if len(warehouse_ids) > 1:
                raise osv.except_osv('Error','Hay demasiadas referencias para la bodega de origen')
                return False
            if picking.backorder_id:
                origen_bo = False
                mismo_origen_bo = True
                for move_bo in picking.backorder_id.move_lines:
                    if not origen_bo:
                        origen_bo = move_bo.location_id.id
                    else:
                        if move_bo.location_id.id != origen_bo:
                            mismo_origen_bo = False
                if mismo_origen_bo and origen_bo:
                    origen = origen_bo
                else:
                    raise osv.except_osv('Error','No se puede obtener la ubicacion de origen (Origen Back Order)')
                    return False
            else:
                raise osv.except_osv('Error','No se puede obtener la ubicacion de origen (Back Order)')
                return False

        #Sobrante: cuando van mas productos fisicos de los que se
        #informa en el documento (albaran)
        if tipo_ajuste == 'sobrante':
            origen_id = origen
            destino_id = destino
        #Faltante: cuando van menos productos fisicos de los que se
        #informa en el documento (albaran)
        if tipo_ajuste == 'faltante':
            origen_id = destino
            destino_id = origen

        return origen_id, destino_id

    def crear_albaran_ajuste(self, cr, uid, ids, context=None):

        if len(ids) > 1:
            raise osv.except_osv('Error','Hay demasiadas referencias. (Albaran)')
            return False

        ade = self.browse(cr, uid, ids[0], context)

        if ade.tipo_ajuste == 'ninguno':
            raise osv.except_osv('Error','Hay un error y no se puede continuar (Tipo de ajuste no puede ser Ninguno)')
            return False

        if context is None:
            context = {} 
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            raise osv.except_osv('Error','Hay un error y no se puede continuar (Falta referencia)')
            return False

        pick_obj = self.pool.get('stock.picking')
        picking = pick_obj.browse(cr, uid, record_id, context)
        pick_vals = {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking'),
            'origin': picking.origin,
            'date': time.strftime('%Y-%m-%d'),
            'type': 'out',
            'state': 'draft',
            'move_type': picking.move_type,
            'sale_id': picking.sale_id and picking.sale_id.id or False,
            'partner_id': picking.partner_id and picking.partner_id.id or False,
            'note': picking.note,
            'invoice_state': picking.invoice_state or 'none',
            'company_id': picking.company_id.id,
            'backorder_id': picking.id,
            'tipo_envio_mc': 'ajuste',
            'recolector_id': picking.recolector_id and picking.recolector_id.id or False
        }
        new_pick_id = pick_obj.create(cr, uid, pick_vals)

        tipo_ajuste = ade.tipo_ajuste

        origen, destino = self.chequea_ubicacion_origen_destino(cr, uid, ids, picking, tipo_ajuste, False, context)

        if not origen or not destino:
            raise osv.except_osv('Error','Hay un error y no se puede continuar (origen o destino)')
            return False

        sm_obj = self.pool.get('stock.move')
        for la in ade.lineas_ajuste_ids:
            move_vals = {
                'picking_id': new_pick_id,
                'name': la.product_id.name,
                'product_id': la.product_id.id,
                'product_qty': la.quantity,
                'product_uos_qty': la.quantity,
                'product_uom': la.product_id.uom_id and la.product_id.uom_id.id or False,
                'product_uos': la.product_id.uom_id and la.product_id.uom_id.id or False,
                'location_id': origen,
                'location_dest_id': destino,
                'product_serial_number_ids': [],
            }
            sm_obj.create(cr, uid, move_vals)
        vals_reg = {
            'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
            'alb_origen': picking.name,
            'alb_destino': pick_vals.get('name', False),
            'usuario': self.pool.get('res.users').browse(cr, uid, uid).name or False,
            'doc_origen': picking.origin,
        }
        self.pool.get('registro.ajuste.stock').create(cr, uid, vals_reg)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Albaran de Ajuste',
            'res_model': 'stock.picking.out',
            'res_id': new_pick_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

ajuste_de_entrega()
