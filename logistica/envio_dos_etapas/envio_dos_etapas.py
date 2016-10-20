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
from openerp import netsvc, tools
import time

import logging

class registro_ajuste_stock(osv.osv):
    _name = "registro.ajuste.stock"
    _order = 'id desc'

    _columns = {
        'name': fields.char('Nombre', readonly=True),
        'fecha': fields.datetime('Fecha', readonly=True),
        'alb_origen': fields.char('Albaran origen', readonly=True),
        'alb_destino': fields.char('Albaran Destino', readonly=True),
        'usuario': fields.char('Usuario', readonly=True),
        'doc_origen': fields.char('Doc. origen', readonly=True),
    }

registro_ajuste_stock()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'tipo_envio_mc': fields.selection([('normal','Normal'),('ajuste','Ajuste'),],'Envio/Ajuste', readonly=True, select=True),
        'recolector_id': fields.many2one('res.users', 'Recolector', track_visibility='onchange', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'act_destino': fields.boolean('Actualizacion Destino'),
        'entregado': fields.boolean('Entregado'),
        'create_uid': fields.many2one('res.users', 'Creador'),
        'write_uid': fields.many2one('res.users', 'Modificador'),
    }

    _defaults = {
        'tipo_envio_mc': 'normal',
        'act_destino': False,
        'entregado': False,
    }

    def check_customer_destination(self, cr, uid, ids):
        location_xml_id = 'stock_location_customers'
        mod_obj = self.pool.get('ir.model.data')
        location_id = False
        try:
            location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
        except (orm.except_orm, ValueError):
            location_id = False
        destination_customer = True
        if location_id:
            for pick in self.browse(cr, uid, ids):
                for move in pick.move_lines:
                    if move.location_dest_id.id != location_id:
                        destination_customer = False
        if destination_customer and location_id:
            self.write(cr, uid, ids, {'entregado': True})
            return True
        return False

    def entregado_met(self, cr, uid, ids, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        stock_move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        ccd = self.check_customer_destination(cr, uid, ids)
        if ccd:
            return True
        for pick in self.browse(cr, uid, ids, context):
            #Crear un albaran de entrega
            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking')
            create_vals = {
                'name': pick_name,
                'origin': pick.origin,
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'internal',
                'state': 'auto',
                'move_type': pick.move_type,
                'sale_id': pick.sale_id and pick.sale_id.id or None,
                'partner_id': pick.partner_id and pick.partner_id.id or None,
                'note': pick.note,
                'invoice_state': pick.invoice_state or 'none',
                'company_id': pick.company_id.id,
                'backorder_id': pick.id,
                'tipo_envio_mc': 'normal',
                'recolector_id': pick.recolector_id and pick.recolector_id.id or None
            }
            new_pick_id = self.create(cr, uid, create_vals)
            #Crear/copiar movimientos de stock
            for sm in pick.move_lines:
                destino_id = False
                warehouse_ids = warehouse_obj.search(cr, SUPERUSER_ID, [('lot_input_id','=',sm.location_dest_id.id)])
                for wh in warehouse_obj.browse(cr, SUPERUSER_ID, warehouse_ids):
                    if wh.company_id.id == sm.location_dest_id.company_id.id:
                        destino_id = wh.lot_stock_id.id
                if not destino_id:
                    raise osv.except_osv('Error!', 'No se puede obtener la ubicacion de destino, debe estar en la compania correcta.')
                    return False
                d = {
                    'picking_id': new_pick_id,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'date_expected': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'location_id': sm.location_dest_id.id,
                    'location_dest_id': destino_id,
                    'tracking_id': False,
                    'state': 'draft',
                }
                stock_move_obj.copy(cr, uid, sm.id, d, context=context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', new_pick_id, 'button_confirm', cr)
            picking_obj.force_assign(cr, uid, [new_pick_id], context)
            self.action_move(cr, uid, [new_pick_id])
            self.action_done(cr, uid, [new_pick_id])
            self.write(cr, uid, [pick.id], {'entregado': True})
        return True

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"

    _columns = {
        'tipo_envio_mc': fields.selection([('normal','Normal'),('ajuste','Ajuste'),],'Envio/Ajuste', readonly=True, select=True),
        'recolector_id': fields.many2one('res.users', 'Recolector', track_visibility='onchange', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'act_destino': fields.boolean('Actualizacion Destino'),
        'entregado': fields.boolean('Entregado'),
        'create_uid': fields.many2one('res.users', 'Creador'),
        'write_uid': fields.many2one('res.users', 'Modificador'),
    }

    def entregado_met(self, cr, uid, ids, context=None):
        res = self.pool.get('stock.picking').entregado_met(cr, uid, ids, context)
        return res

    _defaults = {
        'tipo_envio_mc': 'normal',
        'act_destino': False,
        'entregado': False,
    }

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"

    _columns = {
        'tipo_envio_mc': fields.selection([('normal','Normal'),('ajuste','Ajuste'),],'Envio/Ajuste', readonly=True, select=True),
        'recolector_id': fields.many2one('res.users', 'Recolector', track_visibility='onchange', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'act_destino': fields.boolean('Actualizacion Destino'),
        'entregado': fields.boolean('Entregado'),
        'create_uid': fields.many2one('res.users', 'Creador'),
        'write_uid': fields.many2one('res.users', 'Modificador'),
    }

    _defaults = {
        'tipo_envio_mc': 'normal',
        'act_destino': False,
        'entregado': False,
    }

    def entregado_met(self, cr, uid, ids, context=None):
        res = self.pool.get('stock.picking').entregado_met(cr, uid, ids, context)
        return res

class stock_move(osv.osv):
    _inherit = "stock.move"

    SELECTION_LIST = [
        ('ajuste','Ajuste'),
        ('normal','Normal'),
    ]

    def _tipo_envio_mc(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict()
        for sm in self.browse(cr, uid, ids, context=context):
            if sm.picking_id:
                result[sm.id] = sm.picking_id.tipo_envio_mc
            else:
                result[sm.id] = 'normal'
        return result

    def _recolector_id(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict()
        for sm in self.browse(cr, uid, ids, context=context):
            if sm.picking_id:
                result[sm.id] = sm.picking_id.recolector_id.id
            else:
                result[sm.id] = False
        return result

    def _albaran_relacionado(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict()
        for sm in self.browse(cr, uid, ids, context=context):
            if sm.picking_id:
                if sm.picking_id.backorder_id:
                    result[sm.id] = sm.picking_id.backorder_id.id
                else:
                    result[sm.id] = False
            else:
                result[sm.id] = False
        return result

    _columns = {
        'create_uid': fields.many2one('res.users', 'Creador'),
        'write_uid': fields.many2one('res.users', 'Modificador'),
        'recolector_id': fields.function(_recolector_id, multi=False, type='many2one', relation='res.users', string='Recolector', store=True),
        'tipo_envio_mc': fields.function(_tipo_envio_mc, multi=False, type='selection', selection=SELECTION_LIST, string='Tipo envio MC', store=True),
        'albaran_relacionado_id': fields.function(_albaran_relacionado, multi=False, type='many2one', relation='stock.picking', string='Albaran relacionado', store=True),
    }

    def _default_location_source(self, cr, uid, context=None):

        picking_type = context.get('picking_type')

        location_id = super(stock_move, self)._default_location_source(cr, uid, context)

        if picking_type == 'in':
            return location_id

        company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        location_company_id = self.pool.get('stock.location').browse(cr, SUPERUSER_ID, location_id, context).company_id.id

        if location_company_id != company_id:
            cw_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id','=',company_id)])
            if cw_ids:
                location_id = self.pool.get('stock.warehouse').browse(cr, uid, cw_ids[0], context).lot_stock_id.id

        return location_id

    def _default_location_destination(self, cr, uid, context=None):

        picking_type = context.get('picking_type')

        location_id = super(stock_move, self)._default_location_destination(cr, uid, context)

        #Si el movimiento es de tipo in (entrada) o internal (interno)
        #utilizamos la ubicacion de stock de la compania en la que nos
        #encontramos como ubicacion de destino. cw_ids = Company Warehouse
        if picking_type in ('in', 'internal'):
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
            cw_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id','=',company_id)])
            if cw_ids:
                location_id = self.pool.get('stock.warehouse').browse(cr, uid, cw_ids[0], context).lot_stock_id.id

        #Si hay direccion de destino (address_out_id) utilizamos esa ubicacion.
        if context.get('address_out_id', False):
            ubicacion_destino = self.pool.get('res.partner').browse(cr, uid, context['address_out_id'], context).ubicacion_destino_id
            if ubicacion_destino:
                location_id = ubicacion_destino.id

        return location_id

    _defaults = {
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }

class sale_order(osv.Model):
    _inherit = "sale.order"

    def action_ship_create(self, cr, uid, ids, context=None):

        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        journal_obj = self.pool.get('stock.journal')
        actualizar_destino = False
        compania_usuario = self.pool.get('res.users').browse(cr, uid, uid).company_id.id

        res = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)

        stock_move_ids = []
        pick_ids = []

        for order in self.browse(cr, uid, ids, context=context):
            diario = journal_obj.search(cr, uid, [('company_id','=',compania_usuario)])
            valores_escribir = dict()
            valores_escribir['act_destino'] = True
            if diario:
                valores_escribir['stock_journal_id'] = diario[0]
            pick_ids += [picking.id for picking in order.picking_ids]
            for line in order.order_line:
                stock_move_ids += [move.id for move in line.move_ids]
            destino = order.partner_shipping_id.ubicacion_destino_id.id
            move_obj.write(cr, uid, stock_move_ids, {'location_dest_id':destino})
            picking_obj.write(cr, uid, pick_ids, valores_escribir)

        stock_move_ids = []
        pick_ids = []
        return res


class pos_order(osv.osv):
    _inherit = 'pos.order'

    def write(self, cr, uid, ids, vals, context=None):
        res = super(pos_order, self).write(cr, uid, ids, vals, context=context)
        pick_obj = self.pool.get('stock.picking')
        for po in self.browse(cr, uid, ids):
            if po.picking_id:
                if not po.picking_id.entregado:
                    pick_obj.write(cr, uid, [po.picking_id.id], {'entregado':True})
        return res

