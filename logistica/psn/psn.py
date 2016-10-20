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

from osv import osv, fields
from tools.translate import _
from datetime import datetime
import time
import netsvc

#----------------------------------------------------------
# Product Serial Number
#----------------------------------------------------------
class product_serial_number(osv.Model):
    """Product Serial Number"""
    _name = 'product.serial.number'
    _description = 'Product Serial Number'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id, line.name))
        return res

    def create(self, cr, uid, vals, context=None):
        exist_psn = self.search(cr, uid, [('name','=',vals['name']),('product_id','=',vals['product_id'])])
        psn_obj = self.pool.get('product.serial.number')
        if exist_psn:
            psn = []
            for psn_item in psn_obj.browse(cr, uid, exist_psn):
                psn.append(psn_item.product_id.default_code)
            psn = str(psn)
            productid = vals.get('product_id', False)
            if not productid:
                raise osv.except_osv(_('Error!'), _('No se puede crear un numero de serie sin un producto asociado'))
                return False
            for product in self.pool.get('product.product').browse(cr, uid, [vals['product_id']]):
                if product.psn_unique_ftp:
                    raise osv.except_osv(_('Error!'), _('La serie %s  ya existe para este producto: %s ')%(vals['name'],product.default_code))
                    return False
                if product.psn_unique:
                    raise osv.except_osv(_('Error!'), _('La serie %s  ya existe para el/los siguiente(s) producto(s): %s y debe ser unica.')%(vals['name'],psn))
                    return False
        return super(product_serial_number, self).create(cr, uid, vals, context)

    _columns = {
        'name': fields.char('Numero de Serie', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Producto', required=True),
        'location_id': fields.many2one('stock.location', 'Ubicacion'),
        'create_uid': fields.many2one('res.users', 'Creador'),
        'write_uid': fields.many2one('res.users', 'Modificador'),
        'create_date': fields.datetime('Fecha creacion', readonly=True),
        'write_date': fields.datetime('Fecha modificacion', readonly=True),
        'move_ids': fields.many2many('stock.move', 'serialnumber_stockmove_rel', 'serialnumber_id', 'move_id', 'Movimientos de stock'),
        'expiration_date': fields.date('Fecha de expiracion'),
        'import_date': fields.datetime('Fecha Importacion'),
        'to_import': fields.boolean('Para importar'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lote'),
        'pvp': fields.related('product_id','lst_price',type='float',string='Precio'),
        'costo': fields.related('product_id','standard_price',type='float',string='Costo'),
        'active_move_id': fields.many2one('stock.move', 'Stock Move Activo'),
        'state': fields.selection([('draft', 'Nuevo'),
                                               ('cancel', 'Cancelado'),
                                               ('waiting', 'Esperando'),
                                               ('confirmed', 'Esperando disponibilidad'),
                                               ('assigned', 'Disponible'),
                                               ('done', 'Realizado'),],'Estado'),
        'last_move_id': fields.many2one('stock.move', 'Ultimo Stock Move'),
        'picking_id': fields.related('last_move_id','picking_id',type='many2one',relation='stock.picking',string='Albaran'),
        'active': fields.boolean('Activo'),
    }

    _defaults = {
        'to_import': False,
        'active_move_id': False,
        'active': True,
        'state': 'draft'
    }

    def unlink(self, cr, uid, ids, context=None):
        if context:
            ctx = context.copy()
        else:
            ctx = {}
        for psn in self.browse(cr, uid, ids, context=ctx):
            if psn.move_ids:
                raise osv.except_osv('Error','No puede eliminar un numero de serie (%s) que este asociado a algun movimiento de stock, pero lo puede desactivar.'%psn.name)
                return False
        return super(product_serial_number, self).unlink(cr, uid, ids, context=ctx)

product_serial_number()

#----------------------------------------------------------
# Product Serial Number File
#----------------------------------------------------------
class product_serial_number_file(osv.Model):
    """Product Serial Number File"""
    _name = 'product.serial.number.file'
    _description = 'Product Serial Number File'

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'data': fields.text('Contenido'),
        'picking_id': fields.many2one('stock.picking', 'Albaran'),
    }

product_serial_number_file()

#----------------------------------------------------------
# Stock Move
#----------------------------------------------------------
class stock_move(osv.Model):
    """Product Serial Number on Stock Move"""
    _inherit = 'stock.move'

    _columns = {
        'product_serial_number_ids': fields.many2many('product.serial.number', 'stockmove_serialnumber_rel', 'move_id', 'serialnumber_id','Numero de serie'),
    }

    def _check_expiration_date(self, cr, uid, ids, sn_ids, context=None):
        psn_obj = self.pool.get('product.serial.number')
        for sn in psn_obj.browse(cr, uid, sn_ids):
            if sn.expiration_date:
                expiration_date = datetime.strptime(sn.expiration_date, '%Y-%m-%d')
                if expiration_date < datetime.now():
                    raise osv.except_osv(_('Error!'), _('Esta serie %s ya expiro!')%(sn.name))
                    return False
        return True

    def create_psn_file(self, cr, uid, ids, picking_id, context=None):
        picking_obj = self.pool.get('stock.picking')
        psn_file_ids = []
        for picking in picking_obj.browse(cr, uid, [picking_id], context=context):
            if not picking.psn_file_ids:
                psn_file_obj = self.pool.get('product.serial.number.file')
                file_name = picking.name.replace('/','')
                file_content = "\"Serial Number\",\"SKU\",\"Product\"\n"
                for psn in picking.psn_ids:
                    file_content += "\""+psn.name+"\""+","+"\""+psn.product_id.default_code+"\""+","+"\""+psn.product_id.name+"\""+"\n"
                create_vals = {
                    'name': file_name,
                    'picking_id': picking.id,
                    'data': file_content,
                }
                psn_file_id = psn_file_obj.create(cr, uid, create_vals, context=context)
                psn_file_ids.append(psn_file_id)
        return psn_file_ids

    def update_picking_with_serial_numbers(self, cr, uid, ids, move, context=None):
        if not move.picking_id.psn_ids:
            serial_list = []
            for move in move.picking_id.move_lines:
                for serial in move.product_serial_number_ids:
                    serial_list.append(serial.id)
            picking_obj = self.pool.get('stock.picking')
            picking_obj.write(cr, uid, [move.picking_id.id], {'psn_ids': [(6, move.picking_id.id, serial_list)],})
        self.create_psn_file(cr, uid, ids, move.picking_id.id, context=context)
        return True

    def update_product_serial_number(self, cr, uid, ids, move):
        #actualiza la ubicacion y agrega el movimiento al numero de serie
        psn_obj = self.pool.get('product.serial.number')
        psnids = []
        for s in move.product_serial_number_ids:
            psnids.append(s.id)
        if move.prodlot_id:
            prodlot_id = move.prodlot_id.id
        else:
            prodlot_id = False
        self._check_expiration_date(cr, uid, ids, psnids)
        write_vals = {
            'location_id': move.location_dest_id.id,
            'move_ids': [(4, move.id,)],
            'prodlot_id': prodlot_id,
            'last_move_id': move.id,
            'state': 'done',
        }
        psn_obj.write(cr, uid, psnids, write_vals)
        return True

    def _check_origin(self, cr, uid, ids, move):
        #esta comprobacion funciona para devolver productos
        move_obj = self.pool.get('stock.move')
        args = [('move_dest_id','=', move.id),]
        move_child_ids = move_obj.search(cr, uid, args, offset=0, limit=None, order=None, context=None, count=False)
        ok1 = False
        ok2 = False
        ok3 = False
        for childmove in move_obj.browse(cr, uid, move_child_ids):
            if childmove.product_id.id == move.product_id.id:
                ok1 = True
            if childmove.product_qty == move.product_qty:
                ok2 = True
            if childmove.location_dest_id.id == move.location_dest_id.id:
                ok3 = True
            if (ok1 == True) and (ok2 == True) and (ok3 == True):
                return True
        return False

    def _check_return_in_stock_move(self, cr, uid, ids, move):
        #verifica que sea albaran de devolucion
        ret_move = False
        if ('return' in move.picking_id.name) or ('return' in move.name):
            ret_move = True
        if move.product_serial_number_ids:
            psn_loc = True
        else:
            psn_loc = False
        for psn in move.product_serial_number_ids:
            usage = psn.location_id.usage
            if usage != 'customer':
                psn_loc = False
        if psn_loc and ret_move:
            return True
        return False

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        partial_datas=''
        picking_ids = []
        move_ids = []
        partial_obj=self.pool.get('stock.partial.picking')
        wf_service = netsvc.LocalService("workflow")
        partial_id=partial_obj.search(cr,uid,[])
        if partial_id:
            partial_datas = partial_obj.read(cr, uid, partial_id, context=context)[0]
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                if move.move_dest_id.state in ('waiting', 'confirmed'):
                    if move.prodlot_id.id and move.product_id.id == move.move_dest_id.product_id.id:
                        self.write(cr, uid, [move.move_dest_id.id], {'prodlot_id':move.prodlot_id.id})
                    self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                    if move.move_dest_id.picking_id:
                        wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                    if move.move_dest_id.auto_validate:
                        self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._create_product_valuation_moves(cr, uid, move, context=context)
            prodlot_id = partial_datas and partial_datas.get('move%s_prodlot_id' % (move.id), False)
            if prodlot_id:
                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_id}, context=context)
            if move.state not in ('confirmed','done','assigned'):
                todo.append(move.id)

            #product serial number
            if move.product_id.psn == True:
                origin = self._check_origin(cr, uid, ids, move)
                return_move = self._check_return_in_stock_move(cr, uid, ids, move)
                if origin == False:
                    if not move.product_serial_number_ids:
                        raise osv.except_osv(_('Error!'), _('Este producto ( %s ) usa numero de serie!!!')%(move.product_id.default_code))
                        return False
                    if abs(move.product_qty) != len(move.product_serial_number_ids) and not(return_move):
                        raise osv.except_osv(_('Error!'), _('Hay una diferencia entre cantidad %s y cantidad de numeros de serie %s')%(str(int(move.product_qty)),str(len(move.product_serial_number_ids))))
                        return False
                self.update_product_serial_number(cr, uid, ids, move)
                self.update_picking_with_serial_numbers(cr, uid, ids, move, context=context)
            #product serial number

        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        for id in move_ids:
             wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True

    def action_cancel(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.product_serial_number_ids:
                psn_obj = self.pool.get('product.serial.number')
                serial_list = []
                for serial in move.product_serial_number_ids:
                    serial_list.append(serial.id)
                write_vals = {
                    'state': 'cancel',
                }
                psn_obj.write(cr, uid, serial_list, write_vals) 
        return super(stock_move, self).action_cancel(cr, uid, ids, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.product_serial_number_ids:
                psn_obj = self.pool.get('product.serial.number')
                serial_list = []
                for serial in move.product_serial_number_ids:
                    serial_list.append(serial.id)
                write_vals = {
                    'state': 'confirmed',
                }
                psn_obj.write(cr, uid, serial_list, write_vals)
        return super(stock_move, self).action_confirm(cr, uid, ids, context=context)

    def action_assign(self, cr, uid, ids, *args):
        for move in self.browse(cr, uid, ids):
            if move.product_serial_number_ids:
                psn_obj = self.pool.get('product.serial.number')
                serial_list = []
                for serial in move.product_serial_number_ids:
                    serial_list.append(serial.id)
                write_vals = {
                    'state': 'assigned',
                }
                psn_obj.write(cr, uid, serial_list, write_vals)
        return super(stock_move, self).action_assign(cr, uid, ids, *args)

stock_move()

#----------------------------------------------------------
# Product
#----------------------------------------------------------
class product_product(osv.Model):
    """Product Serial Number on Product"""
    _inherit = 'product.product'

    _columns = {
        'psn': fields.boolean('Usa Numero de Serie',
                                             help="Obliga a ingresar un numero de serie para todos los movimientos de stock del producto."),
        'psn_unique': fields.boolean('Usa Numero de Serie Unico',
                                             help="El numero de serie debe ser unico y no pueden existir mas que sean iguales."),
        'psn_unique_ftp': fields.boolean('Usa Numero de Serie Unico para este producto',
                                             help="El numero de serie debe ser unico para este producto, pero puede existir el mismo para otro producto."),
        'stockmove_ids': fields.one2many('stock.move', 'product_id', 'Movimientos de stock'),
        'serialnumber_ids': fields.one2many('product.serial.number', 'product_id', 'Numeros de serie'),
    }

product_product()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.Model):
    """Stock picking"""
    _inherit = 'stock.picking'
    _table = 'stock_picking'

    _columns = {
        'psn_ids': fields.many2many('product.serial.number', 'stockpicking_serialnumber_rel', 'picking_id', 'serialnumber_id','Numeros de serie'),
        'psn_file_ids': fields.one2many('product.serial.number.file','picking_id','PSN File'),
    }

    _defaults = {
        'psn_ids': False,
    }

stock_picking()

#----------------------------------------------------------
# Stock Picking In
#----------------------------------------------------------
class stock_picking_in(osv.Model):
    """Stock picking"""
    _inherit = 'stock.picking.in'
    _table = 'stock_picking'

    _columns = {
        'psn_ids': fields.many2many('product.serial.number', 'stockpicking_serialnumber_rel', 'picking_id', 'serialnumber_id','Numeros de serie'),
        'psn_file_ids': fields.one2many('product.serial.number.file','picking_id','PSN File'),
    }

    _defaults = {
        'psn_ids': False,
    }

stock_picking_in()

#----------------------------------------------------------
# Stock Picking Out
#----------------------------------------------------------
class stock_picking_out(osv.Model):
    """Stock picking"""
    _inherit = 'stock.picking.out'
    _table = 'stock_picking'

    _columns = {
        'psn_ids': fields.many2many('product.serial.number', 'stockpicking_serialnumber_rel', 'picking_id', 'serialnumber_id','Numeros de serie'),
        'psn_file_ids': fields.one2many('product.serial.number.file','picking_id','PSN File'),
    }

    _defaults = {
        'psn_ids': False,
    }

stock_picking_out()

