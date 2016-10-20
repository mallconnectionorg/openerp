# -*- coding: utf-8 -*-
##############################################################################
#
#   Cesar Lopez
#   Copyright (C) 2011 Cesar Lopez(<http://www.ronin.cl>).
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
import base64
import cStringIO
from openerp.tools.misc import get_iso_codes
from openerp import tools

from osv import fields, osv
from tools.translate import _
from datetime import datetime
import time

#----------------------------------------------------------
# Product Serial Number
#----------------------------------------------------------
class product_serial_number(osv.Model):
    """Product Serial Number"""
    _inherit = 'product.serial.number'


    def action_unlink_serial_id(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not  (context.get('smid', [])):
            raise osv.except_osv(_('Error!'), _('No puede faltar el movimiento de stock'))
            return False
        else:
            moveid = context.get('smid', [])
        if not (context.get('sid', [])):
            raise osv.except_osv(_('Error!'), _('No puede faltar el numero de serie'))
            return False
        else:
            serialid = context.get('sid', [])
        move_obj = self.pool.get('stock.move')
        psn_obj = self.pool.get('product.serial.number')
        for move in move_obj.browse(cr, uid, [moveid]):
            if (move.state == 'done') or (move.state == 'cancel'):
                raise osv.except_osv(_('Error!'), _('No puedes eliminar series asociadas a movimientos de stock en estado realizado o cancelado'))
                return False
            serial_list = []
            for serial in move.product_serial_number_ids:
                serial_list.append(serial.id)
                if serialid in serial_list:
                    serial_list.remove(serialid)
            serial_list.sort()
            lenids = len(serial_list)
            move_obj.write(cr, uid, [move.id], {'product_serial_number_ids': [(6, move.id, serial_list)], 'product_qty': lenids, 'product_uos_qty': lenids})
        for serialnumber in self.browse(cr, uid, [serialid]):
            if not serialnumber.location_id:
                psn_obj.unlink(cr, uid, [serialnumber.id], context=None)
        return True

product_serial_number()

#----------------------------------------------------------
# Product Serial Numbers Wizard (Stock Move)
#----------------------------------------------------------
class product_serial_number_wizard(osv.osv_memory):
    _name = "product.serial.number.wizard"
    _description = "Product Serial Number Wizard"

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for psnw in self.browse(cr, uid, ids, context=context):
            res.append((psnw.id, psnw.move_id.name))
        return res

    def _product_default_get(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        for move in move_obj.browse(cr, uid, [context['active_id']]):
            res = move.product_id.id
        return res

    _columns = {
        'move_id': fields.many2one('stock.move','Referential Move ID'),
        'product_id': fields.many2one('product.product', 'Product',),
        'line_ids': fields.one2many('serial.number.wizard', 'psnw_id', 'Serial Numbers'),
        'expiration_date': fields.date('Expiration Date'),
        'type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')],'Shipping Type'),
    }

    _defaults = {
        'move_id': lambda x, y, z, c: c.get('active_id', False),
        'product_id': lambda self, cr, uid, c: self._product_default_get(cr, uid, [c.get('active_id', False)], context=c),
        'type': lambda x, y, z, c: c.get('picking_type', False),
    }

    def _check_product_id(self, cr, uid, ids, context=None):
        for psnw in self.browse(cr, uid, ids):
            if not psnw.product_id:
                return False
        return True


    def _check_return(self, cr, uid, ids, move, sn_loc):
        loc_obj = self.pool.get('stock.location')
        ret_move = False
        if ('return' in move.picking_id.name) or ('return' in move.name):
            ret_move = True
        if sn_loc:
            for sl in loc_obj.browse(cr, uid, [sn_loc]):
                usage = sl.usage
                if (usage == 'supplier') or (usage == 'customer') and ret_move:
                    return True
        return False

    def _check_duplication_in_stock_picking(self, cr, uid, ids, picking_id, serials, context=None):
        pick_obj = self.pool.get('stock.picking')
        picking = pick_obj.browse(cr, uid, picking_id)
        allserialsinpicking = []
        for move in picking.move_lines:
            for serial in move.product_serial_number_ids:
                allserialsinpicking.append(serial.id)
        completelist = allserialsinpicking + serials
        for s in serials:
            repite = completelist.count(s)
            if repite > 1:
                psn_obj = self.pool.get('product.serial.number')
                psnread = psn_obj.read(cr, uid, s)
                raise osv.except_osv(_('Error!'), _('La serie %s ya existe en esta guia!!!')%(psnread['name']))
                return False
        return True

    def _check_location(self, cr, uid, ids, move, eserialids):
        sn_obj = self.pool.get('product.serial.number')
        newlist = []
        for esid in eserialids:
            if esid:
                newlist.append(esid)
        for sn in sn_obj.browse(cr, uid, newlist):
            if sn.location_id:
                ret = self._check_return(cr, uid, ids, move, sn.location_id.id)
                if (sn.location_id.id != move.location_id.id) and (ret == False):
                    raise osv.except_osv(_('Error!'), _('El numero de serie %s no esta en esta ubicacion %s, esta en %s')%(sn.name, move.location_id.name, sn.location_id.name))
                    return False
        return True

    def close_serial_number_wizard(self, cr, uid, ids, context=None):
        psn_obj = self.pool.get('product.serial.number')
        move_obj = self.pool.get('stock.move')
        for move in move_obj.browse(cr, uid, [context['active_id']]):
            if move.product_id.psn == False:
                raise osv.except_osv(_('Error!'), _('Este producto ( %s ) no usa numero de serie!!!')%(move.product_id.default_code))
                return False
            for psnw in self.browse(cr, uid, ids):
                lines = [c for c in psnw.line_ids if c]
                lines.sort()
                ltemp = []
                name_list = []
                for line1 in lines:
                    if line1.name != False and line1.name != "":
                        name_list.append(line1.name)
                for line in lines:
                    if line.name != False and line.name != "":
                        psn_exist = False
                        psn_exist = psn_obj.search(cr, uid, [('name','=',line.name),('product_id','=',move.product_id.id),('active','=',True)])
                        if psn_exist:
                            psn_reads = False
                            psn_reads = psn_obj.read(cr, uid, psn_exist)
                            psn_read = psn_reads[0]
                            sn_product_tuple_list = []
                            product_ids_reads = []
                            for psnr in psn_reads:
                                temp_list = [psnr['id'],psnr['product_id'][0]]
                                sn_product_tuple_list.append(tuple(temp_list))
                                product_ids_reads.append(psnr['product_id'][0])
                            if move.product_id.id in product_ids_reads \
                            and (move.picking_id.type == 'in') and move.product_id.psn_unique_ftp:
                                raise osv.except_osv(_('Error!'), _('El numero de serie (%s) existe para este producto ( %s ) y debe ser unico para el SKU')%(line.name,move.product_id.default_code))
                                return False
                            elif move.product_id.id in product_ids_reads \
                            and (move.picking_id.type == 'in') and move.product_id.psn_unique:
                                raise osv.except_osv(_('Error!'), _('El numero de serie (%s) existe para este producto ( %s ) y debe ser unico.')%(line.name,move.product_id.default_code))
                                return False
                            elif move.product_id.id not in product_ids_reads and (move.picking_id.type in ['internal','out']):
                                raise osv.except_osv(_('Error!'), _('El numero de serie (%s) no existe para este producto ( %s )')%(line.name,move.product_id.default_code))
                                return False
                            elif move.picking_id.type in ['internal','out'] and move.product_id.id in product_ids_reads \
                            and not move.product_id.psn_unique and not move.product_id.psn_unique_ftp:
                                veces = name_list.count(line.name)
                                multi_list = []
                                for i in range(veces):
                                    for psn in psn_reads:
                                        if (len(multi_list) < veces) and (psn['id'] not in ltemp):
                                            ltemp.append(psn['id'])
                                            multi_list.append(psn['id'])
                            else:
                                ltemp.append(int(psn_read['id']))
                        else:
                            if move.picking_id.type == 'in':
                                vals = {
                                    'name': line.name,
                                    'product_id': move.product_id.id,
                                    'expiration_date': psnw.expiration_date,
                                }
                                serialnumber_id = psn_obj.create(cr, uid, vals, context=context)
                                serialnumber_id = int(serialnumber_id)
                                if serialnumber_id:
                                    ltemp.append(serialnumber_id)
                                else:
                                    raise osv.except_osv(_('Error!'), _('El numero de serie %s no puede ser creado')%(vals['name']))
                                    return False
                            else:
                                raise osv.except_osv(_('Error!'), _('La serie %s no existe o esta inactiva para este producto (%s), solo se pueden crear series desde una guia de entrada o puede editarlas desde el menu para numeros de serie.')%(line.name,move.product_id.default_code))
                                return False
                self._check_location(cr, uid, ids, move, ltemp)
                picking_id = move.picking_id.id
                self._check_duplication_in_stock_picking(cr, uid, ids, picking_id, ltemp, context=context)
            slist = []
            for serialnumber in move.product_serial_number_ids:
                slist.append(serialnumber.id)
            ltemp = ltemp + slist
            ltemp.sort()
            move_obj.write(cr, uid, [move.id], {'product_serial_number_ids': [(6, move.id, ltemp)], 'product_qty': len(ltemp), 'product_uos_qty': len(ltemp)})
            psn_obj.write(cr, uid, ltemp, {'state': move.state})
        return {'type': 'ir.actions.act_window_close'}

    _constraints = [
        (_check_product_id, 'Error, You have a problem with Product ID!!!', ['product_id']),
    ]

product_serial_number_wizard()

#----------------------------------------------------------
# Serial Numbers in Wizard
#----------------------------------------------------------
class serial_number_wizard(osv.osv_memory):
    _name = "serial.number.wizard"
    _description = "Serial number"

    _columns = {
        'name': fields.char('Serial Number', size=64),
        'psnw_id': fields.many2one('product.serial.number.wizard', 'PSNW'),
    }

serial_number_wizard()

#----------------------------------------------------------
# This is for show the serial numbers and let edit its
#----------------------------------------------------------
class show_product_serial_number(osv.osv_memory):
    _name = "show.product.serial.number"
    _description = "show.product.serial.number"

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for spsn in self.browse(cr, uid, ids, context=context):
            res.append((spsn.id, spsn.move_id.name))
        return res

    def _psn_ids_get(self, cr, uid, ids, context=None):
        psn_obj = self.pool.get('product.serial.number')
        res = []
        mid = context.get('active_id', False)
        if mid:
            move_obj = self.pool.get('stock.move')
            for move in move_obj.browse(cr, uid, [mid], context=context):
                for sn in move.product_serial_number_ids:
                    res.append(sn.id)
                psn_obj.write(cr, uid, res, {'active_move_id':move.id, 'active_move_state':move.state})
        return res

    _columns = {
        'move_id': fields.many2one('stock.move', 'Stock Move'),
        'psn_ids': fields.many2many('product.serial.number', 'spsn_stockmove_rel', 'spsn_id', 'psn_id', 'SN'),
    }

    _defaults = {
        'move_id': lambda x, y, z, c: c.get('active_id', False),
        'psn_ids': lambda x, y, z, c: x._psn_ids_get(y, z, [], context=c),
    }


show_product_serial_number()

#-----------------------------------------------------------------------
#Import Product Serial Numbers Wizard
#-----------------------------------------------------------------------
class import_product_serial_number_wizard(osv.osv_memory):
    _name = 'import.product.serial.number.wizard'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for a in self.browse(cr, uid, ids, context=context):
            res.append((a.id, a.name))
        return res

    _columns = {
        'name': fields.char('Nombre', size=64),
        'stock_move_id': fields.many2one('stock.move', 'Movimiento de stock', readonly=True),
        'state': fields.selection([('draft','Borrador'),('done','Hecho')],'Estado'),
    }

    def pre_importar_series(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def importar_series(self, cr, uid, ids, context=None):
        product_id = context.get('product_id', False)
        active_id = context.get('active_id', False)
        if active_id:
            active_id = int(active_id)
        stock_move_obj = self.pool.get('stock.move')
        psn_obj = self.pool.get('product.serial.number')
        for ipsnw in self.browse(cr, uid, ids):
            if product_id:
                search_criteria = [('product_id','=',product_id),('create_uid','=',uid),('to_import','=',True)]
                psn_ids = psn_obj.search(cr, uid, search_criteria, offset=0, limit=None, order=None, context=None, count=False)
            else:
                psn_ids = []
            if psn_ids:
                psn_obj.write(cr, uid, psn_ids, {'to_import':False, 'import_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                stock_move_obj.write(cr, uid, [active_id], {'product_serial_number_ids': [(6, active_id, psn_ids)], 'product_qty': len(psn_ids), 'product_uos_qty': len(psn_ids)})
        return {'type': 'ir.actions.act_window_close'}

    _defaults = {
        'stock_move_id': lambda x, y, z, c: c.get('active_id', False),
        'state': 'draft',
    }

import_product_serial_number_wizard()

#-----------------------------------------------------------------------
#Product Serial Number Export
#-----------------------------------------------------------------------
class psn_export(osv.osv_memory):
    _name = "psn.export"


    _columns = {
            'name': fields.char('File Name', readonly=True),
            'format': fields.char('Format', readonly=True),
            'data': fields.binary('File', readonly=True),
            'state': fields.selection([('choose', 'choose'),('get', 'get')]),
            'picking_id': fields.many2one('stock.picking', 'Albaran'),
    }

    _defaults = { 
        'state': 'choose',
        'format': 'csv',
        'name': 'series.csv',
    }

    def act_getfile(self, cr, uid, ids, context=None):
        picking_id = context.get('active_id', False)
        file_obj = self.pool.get('product.serial.number.file')
        file_ids = file_obj.search(cr, uid, [('picking_id','=',picking_id)])
        if file_ids:
            psn_file = file_obj.browse(cr, uid, file_ids)[0]
            buf = cStringIO.StringIO()
            buf.write(psn_file.data)
            out = base64.encodestring(buf.getvalue())
            buf.close()
            filename_psn = psn_file.name+".csv"
            write_vals = {
                'name': filename_psn,
                'data': out,
            }
            self.write(cr, uid, ids, write_vals, context=context)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'psn.export',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': ids[0],
                'views': [(False, 'form')],
                'target': 'new',
            }
        else:
            self.pool.get('stock.move').create_psn_file(cr, uid, ids, picking_id, context=context)
            self.act_getfile(cr, uid, ids, context=context)
            return self.act_getfile(cr, uid, ids, context=context)

psn_export()
#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.Model):
    """Stock picking"""
    _inherit = 'stock.picking'

    def act_getfile(self, cr, uid, ids, context=None):
        psn_export_obj = self.pool.get("psn.export")
        psn_export_id = psn_export_obj.create(cr, uid, {'picking_id':context.get('active_id',False)}, context=context)
        return psn_export_obj.act_getfile(cr, uid, [psn_export_id], context=context)

stock_picking()

#----------------------------------------------------------
# Stock Picking In
#----------------------------------------------------------
class stock_picking_in(osv.Model):
    """Stock picking"""
    _inherit = 'stock.picking.in'

    def act_getfile(self, cr, uid, ids, context=None):
        psn_export_obj = self.pool.get("psn.export")
        psn_export_id = psn_export_obj.create(cr, uid, {'picking_id':context.get('active_id',False)}, context=context)
        return psn_export_obj.act_getfile(cr, uid, [psn_export_id], context=context)

stock_picking_in()

#----------------------------------------------------------
# Stock Picking Out
#----------------------------------------------------------
class stock_picking_out(osv.Model):
    """Stock picking"""
    _inherit = 'stock.picking.out'

    def act_getfile(self, cr, uid, ids, context=None):
        psn_export_obj = self.pool.get("psn.export")
        psn_export_id = psn_export_obj.create(cr, uid, {'picking_id':context.get('active_id',False)}, context=context)
        return psn_export_obj.act_getfile(cr, uid, [psn_export_id], context=context)

stock_picking_out()
