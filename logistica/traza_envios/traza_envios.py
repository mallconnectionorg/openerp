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
from xhtml2pdf import pisa
from datetime import datetime
from openerp import tools

import logging

class stock_caja_transporte(osv.Model):
    _name = 'stock.caja.transporte'

    material_caja = [
        ('plastico','Plastico'),
        ('carton','Carton'),
        ('madera','Madera'),
        ('otro','Otro'),
    ]

    def _get_volumen_caja(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict()
        for caja in self.browse(cr, uid, ids):
            if caja.ancho and caja.alto and caja.largo:
                res[caja.id] = (caja.ancho * caja.alto * caja.largo) / 1000
            else:
                res[caja.id] = 0.0
        return res


    def _get_cantidad_caja(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict()
        ctx = context.copy()
        warehouse_obj = self.pool.get('stock.warehouse')
        product_obj = self.pool.get('product.product')

        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        warehouse_ids = warehouse_obj.search(cr, uid, [('company_id', '=', company_id)])

        location_ids = []
        for wh in warehouse_obj.browse(cr, uid, warehouse_ids):
            location_ids.append(wh.lot_stock_id.id)

        ctx.update({'location': location_ids, 'states': ('done',), 'what': ('in', 'out')})

        for caja in self.browse(cr, uid, ids, ctx):
            if caja.product_id:
                res[caja.id] = product_obj.get_product_available(cr, uid, [caja.product_id.id], context=ctx)[caja.product_id.id]
            else:
                res[caja.id] = 0.0

        return res


    _columns = {
        'name': fields.char('Caja', size=48, select=True, required=True),
        'material': fields.selection(material_caja, 'Material', select=True, required=True),
        'alto': fields.float('Alto (cm.)'),
        'ancho': fields.float('Ancho (cm.)'),
        'largo': fields.float('Largo (cm.)'),
        'peso': fields.float('Peso (kg.)'),
        'volumen': fields.function(_get_volumen_caja, type='float', string='Volumen (lts.)', store=True),
        'product_id': fields.many2one('product.product', 'Producto'),
        'cantidad': fields.function(_get_cantidad_caja, type='float', string='Cantidad', store=False),
    }

class stock_orden_transporte(osv.Model):
    _name = "stock.orden.transporte"
    _inherit = ['mail.thread']
    _description = "OT"
    _order = "id desc"

    estados_ot = [
        ('esperando','Esperando'),
        ('despachado','Despachado'),
        ('entransito','En transito'),
        ('enreparto','En reparto'),
        ('entregado','Entregado'),
        ('devuelto','Devuelto'),
        ('perdido','Perdido'),
        ('cancelado','Cancelado'),
    ]

    tipo_ot = [
        ('padre','Padre'),
        ('hija','Hija'),
    ]

    def _get_veraccion(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict()
        usuario_obj = self.pool.get('res.users')
        ucid = usuario_obj.browse(cr, uid, uid).company_id and usuario_obj.browse(cr, uid, uid).company_id.id or False
        for sot in self.browse(cr, uid, ids):
            if ucid and sot.company_id:
                if ucid == sot.company_id.id:
                    result[sot.id] = True
                else:
                    result[sot.id] = False
            else:
                result[sot.id] = False
        return result

    _columns = {
        'name': fields.char('Numero', size=48, select=True),
        'ot_id': fields.many2one('stock.orden.transporte', 'OT Padre'),
        'picking_id': fields.many2one('stock.picking','Albaran'),
        'ot_ids': fields.one2many('stock.orden.transporte', 'ot_id', 'OT Hijas', track_visibility='onchange'),
        'state': fields.selection(estados_ot, 'Estado', readonly=True, track_visibility='onchange', select=True),
        'ot_type': fields.selection(tipo_ot, 'Tipo', readonly=True),
        'create_uid': fields.many2one('res.users', 'Creador', readonly=True, select=True),
        'write_uid': fields.many2one('res.users', 'Modificador', readonly=True, select=True),
        'create_date': fields.datetime('Fecha creacion', readonly=True, select=True),
        'write_date': fields.datetime('Fecha modificacion', readonly=True, select=True),
        'company_id': fields.many2one('res.company', 'Compania', select=True),
        'veraccion': fields.function(_get_veraccion, type='boolean', string="Ver accion"),
        'cajas_ids': fields.many2many('stock.caja.transporte', 'caja_ot_rel','ot_id','caja_id', 'Cajas'),
        'estado_albaran': fields.related('picking_id', 'state', type='char', string='Estado Albaran', store=False),
    }

    _defaults = {
        'state': 'esperando',
        'ot_type': 'padre',
        'company_id': False,
    }


    def escribir_objeto_distinta_compania(self, cr, uid, obj, vals):
        logger = logging.getLogger('escribir_objeto_distinta_compania')
        logger.warn('#### SE EJECUTA ####')
        users_obj = self.pool.get('res.users')
        user_browse = users_obj.browse(cr, uid, uid)
        if type(obj) == type(user_browse):
            nombre_objeto = obj._table_name
            objeto = self.pool.get(nombre_objeto)
            compania_objeto = objeto.browse(cr, SUPERUSER_ID, obj.id).company_id.id
            #compania_objeto = obj.company_id.id
            compania_usuario = user_browse.company_id.id
            users_obj.write(cr, SUPERUSER_ID, [uid], {'company_id': compania_objeto})
            objeto.write(cr, uid, [obj.id], vals)
            users_obj.write(cr, SUPERUSER_ID, [uid], {'company_id': compania_usuario})
            logger.warn('#### SE EJECUTO ####')
        return True


    def imprimir_etiquetas(self, cr, uid, ids, context=None):
        datas = dict()
        for ot in self.browse(cr, uid, ids):
            if ot.ot_type == 'hija':
                datas['ids'] = [ot.id]
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'etiqueta.stock.orden.transporte',
                    'datas': datas,
                }

            if ot.ot_type == 'padre':
                ot_ids = []
                ot_ids.append(ot.id)
                for oth in ot.ot_ids:
                    ot_ids.append(oth.id)
                datas['ids'] = ot_ids
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'etiqueta.stock.orden.transporte',
                    'datas': datas,
                }
        return True


    def imprimir_detalle(self, cr, uid, ids, context=None):
        for ot in self.browse(cr, uid, ids):
            datas = dict()
            picking_ids = []

            if ot.ot_type == 'hija':
                if ot.picking_id:
                    picking_ids.append(ot.picking_id.id)

            if ot.ot_type == 'padre':
                for oth in ot.ot_ids:
                    if oth.picking_id:
                        picking_ids.append(oth.picking_id.id)

            datas['ids'] = picking_ids
            if picking_ids:
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'detalle.stock.orden.transporte',
                    'datas': datas,
                }
        return True


    def devuelve_tienda_destino(self, cr, uid, picking):
        res = False
        destino_comun = True
        destino = False
        for move in picking.move_lines:
            if not destino:
                destino = move.location_dest_id
            else:
                if move.location_dest_id.id != destino.id:
                    destino_comun = False
        if destino_comun and destino:
            if destino.company_id:
                shop_ids = self.pool.get('sale.shop').search(cr, SUPERUSER_ID, [('company_id','=',destino.company_id.id)])
                if len(shop_ids) == 1:
                    res = self.pool.get('sale.shop').browse(cr, SUPERUSER_ID, shop_ids[0])
        return res


    def enviar_correo_notificacion(self, cr, uid, correo, adjuntos=None, context=None):
        asunto = correo.get('subject', False)
        cuerpo = correo.get('body', False)
        para = correo.get('email_to')
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(cr, uid, [('name','=','notifica')], context=context)
        mail_server_id = mail_server_ids[0]
        email_from = mail_server_obj.browse(cr, uid, mail_server_id, context=context).smtp_user
        msg = mail_server_obj.build_email(
                    email_from=email_from,
                    email_to=para,
                    reply_to='logistica@mallconnection.com',
                    email_cc=['logistica@mallconnection.com'],
                    body=cuerpo,
                    subject=asunto,
                    attachments = adjuntos,
                    subtype = correo['subtype'],
                    subtype_alternative = correo['subtype_alternative'])
        res = mail_server_obj.send_email(cr, uid, msg,mail_server_id=mail_server_id)
        return res


    def origen_destino(self, cr, uid, picking):
        pick = self.pool.get('stock.picking').browse(cr, SUPERUSER_ID, picking.id)
        mismo_destino = True
        mismo_origen = True
        compania_origen = False
        compania_destino = False
        destino_externo = False
        for move in pick.move_lines:

            if not compania_origen:
                compania_origen = move.company_id.name
            else:
                if compania_origen != move.company_id.name:
                    mismo_origen = False

            if not compania_destino:
                if move.location_dest_id.company_id and not destino_externo:
                    compania_destino = move.location_dest_id.company_id.name
                else:
                    #Chequear que sea ubicacion externa.
                    if move.location_dest_id.usage != 'internal' and not destino_externo:
                        destino_externo = True
                        compania_destino = move.location_dest_id.name
            else:
                if move.location_dest_id.company_id:
                    if compania_destino != move.location_dest_id.company_id.name:
                        mismo_destino = False

        if not mismo_origen or not compania_origen:
            compania_origen = 'Sin Origen'
        if not mismo_destino or not compania_destino:
            compania_destino = 'Sin Destino'
        return compania_origen, compania_destino


    def crear_adjuntos(self, cr, uid, picking):
        origen, destino = self.origen_destino(cr, uid, picking)
        res = []
        contenido_csv = ''
        contenido_csv += '"Origen","%s"\n'%(origen)
        contenido_csv += '"Destino","%s"\n'%(destino)
        contenido_csv += '"Albaran","%s"\n'%(picking.name)
        contenido_csv += '"Guia","%s"\n'%(str(picking.sii_number))
        contenido_csv += '\n'
        contenido_csv += '\n'
        contenido_csv += '"SKU","NOMBRE","CANTIDAD"\n'
        for line in picking.move_lines:
            contenido_csv += '"' + line.product_id.default_code + '",'
            contenido_csv += '"' + line.product_id.name + '",'
            contenido_csv += '"' + str(line.product_qty) + '"\n'
        contenido_csv += '\n'
        contenido_csv += '\n'
        contenido_csv += '"Numero de Serie","SKU","Producto"\n'
        for psn in picking.psn_ids:
            contenido_csv += '"'+psn.name+'"' + ',' + '"'+psn.product_id.default_code+'"' + ',' + '"'+psn.product_id.name+'"' +'\n'
        nombre_csv = picking.name.replace('/','_') + ".csv"
        res.append((nombre_csv, contenido_csv))
        return res


    def crear_mensaje(self, cr, uid, picking):
        origen, destino = self.origen_destino(cr, uid, picking)
        ahora = datetime.now()
        hoy = ahora.strftime('%d-%m-%Y')
        res = ''
        res += 'Hoy ' + hoy + ', '
        res += 'se ha generado un despacho con los siguientes datos: </br>'
        res += '</br>'
        res += '<b>Origen:</b> ' + origen + '</br>'
        res += '<b>Destino:</b> ' + destino + '</br>'
        res += '<b>Resumen:</b> ' + picking.origin + '</br>'
        res += '<b>Orden de Transporte:</b> ' + picking.orden_transporte_id.name + '</br>'
        res += '</br>'
        res += 'El contenido de lo enviado va en el archivo adjunto.' + '</br>'
        res += '</br>'
        res += 'Saludos cordiales,' + '</br>'
        res += 'Departamento de Logistica' + '</br>'
        res += 'Mall Connection' + '</br>'
        return res 


    def crear_notificacion_despacho(self, cr, uid, ot, picking, sale_order, context=None):
        ahora = datetime.now()
        hoy = ahora.strftime('%d-%m-%Y')
        correo = dict()
        correo['email_from'] = 'logistica@mallconnection.com'
        correo['reply_to'] = 'logistica@mallconnection.com'
        correo['body'] = self.crear_mensaje(cr, uid, picking)
        correo['subject'] = 'Despacho [' + picking.name.replace('/','') + '-' + sale_order.name +']' + ' ' + '[' + hoy + ']'
        correo['subtype'] = 'html'
        correo['subtype_alternative'] = 'plain'
        adjuntos = self.crear_adjuntos(cr, uid, picking)
        lista_destinatarios = []
        shop_obj = self.devuelve_tienda_destino(cr, uid, picking)
        if not shop_obj:
            return True
        else:
            for correo_dest in shop_obj.correo_notificacion_ids:
                lista_destinatarios.append(correo_dest.name)
        correo['email_to'] = lista_destinatarios
        return self.enviar_correo_notificacion(cr, uid, correo, adjuntos, context=context)


    def notificar_despacho(self, cr, uid, ids, context=None):
        ot_hijas_ids = []
        for otp in self.browse(cr, uid, ids):
            for oth in otp.ot_ids:
                ot_hijas_ids.append(oth.id)
        for ot in self.browse(cr, uid, ot_hijas_ids):
            if ot.company_id and ot.picking_id:
                if ot.picking_id.sale_id:
                    self.crear_notificacion_despacho(cr, uid, ot, ot.picking_id, ot.picking_id.sale_id, context=context)
        ot_hijas_ids = []
        return True


    def recibir_ot(self, cr, uid, ids, context=None):
        #Metodo creado para que los jefes de tienda reciban sus pedidos.
        picking_obj = self.pool.get('stock.picking')
        for sot in self.browse(cr, SUPERUSER_ID, ids):
            sot_picking_id = sot.picking_id and sot.picking_id.id or False
            if sot.ot_type == 'padre':
                raise osv.except_osv('Error!', 'No puede procesar una OT de tipo Padre.')
                return False
            else:
                if sot_picking_id:
                    if not sot.picking_id.entregado:
                        picking_obj.entregado_met(cr, SUPERUSER_ID, [sot_picking_id], context=context)
                self.write(cr, SUPERUSER_ID, [sot.id], {'state':'entregado'})
        return True


    def todos_entregados(self, cr, uid, ids):
        for sot in self.browse(cr, uid, ids):
            if sot.ot_type == 'hija':
                if sot.ot_id:
                    todas_oth_entregadas = True
                    for oth in self.browse(cr, SUPERUSER_ID, sot.ot_id.id).ot_ids:
                        if oth.state != 'entregado':
                            todas_oth_entregadas = False
                    if todas_oth_entregadas:
                        if sot.ot_id.state != 'entregado':
                            self.write(cr, SUPERUSER_ID, [sot.ot_id.id], {'state':'entregado'})
        return True


    def obtener_ubicacion_origen_y_destino(self, cr, uid, picking):
        location_id = False
        location_dest_id = False
        for move in picking.move_lines:
            location_id = move.location_id.id
            location_dest_id = move.location_dest_id.id
        #Buscar la ubicacion de stock a partir de la ubicacion entrada
        #que es el location_dest_id para este picking
        if location_dest_id:
            wh_ids = self.pool.get('stock.warehouse').search(cr, SUPERUSER_ID, [('lot_input_id','=',location_dest_id)])
            if len(wh_ids) == 1:
                lot_stock_id = self.pool.get('stock.warehouse').browse(cr, SUPERUSER_ID, wh_ids[0]).lot_stock_id
                if lot_stock_id:
                    location_dest_id = lot_stock_id.id
        return location_id, location_dest_id


    def picking_cajas(self, cr, uid, ids, picking_ot, caja_obj, estado=None):
        seq_obj = self.pool.get('ir.sequence')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        origen_picking = picking_ot.name + '-DESPACHO CAJA'
        existe_picking = picking_obj.search(cr, SUPERUSER_ID, [('origin','=',origen_picking),('backorder_id','=',picking_ot.id),('state','!=','cancel')])
        move_ids = []
        if not estado:
            estado = 'despachado'
        if estado == 'despachado':
            if not existe_picking:
                picking_vals = dict()
                picking_vals['name'] = seq_obj.get(cr, uid,'stock.picking')
                picking_vals['origin'] = origen_picking
                picking_vals['type'] = 'internal'
                picking_vals['backorder_id'] = picking_ot.id

                new_picking_id = False
                for caja in caja_obj.browse(cr, uid, ids):
                    if caja.product_id:
                        if not new_picking_id:
                            #Crear stock.picking
                            new_picking_id = picking_obj.create(cr, uid, picking_vals)
                        origen, destino = self.obtener_ubicacion_origen_y_destino(cr, uid, picking_ot)
                        move_vals = dict()
                        move_vals['picking_id'] = new_picking_id
                        move_vals['location_id'] = origen
                        move_vals['location_dest_id'] = destino
                        move_vals['product_id'] = caja.product_id.id
                        move_vals['product_qty'] = 1.0
                        move_vals['state'] = 'confirmed'
                        move_vals['product_uom'] = caja.product_id.uom_id.id
                        move_vals['name'] = caja.product_id.name
                        #Crear stock.move
                        move_obj.create(cr, uid, move_vals)
        if existe_picking and len(existe_picking) == 1:
            for move in picking_obj.browse(cr, uid, existe_picking[0]).move_lines:
                move_ids.append(move.id)
        else:
            return True
        if estado == 'entregado':
            for move in picking_obj.browse(cr, uid, existe_picking[0]).move_lines:
                self.escribir_objeto_distinta_compania(cr, uid, move, {'state':'done'})
            self.escribir_objeto_distinta_compania(cr, uid, picking_obj.browse(cr, uid, existe_picking[0]), {'state':'done'})

        if estado == 'perdido':
            #Buscar la ubicacion Desecho
            ubicacion_desecho_ids = self.pool.get('stock.location').search(cr, uid, [('scrap_location','=',True),('usage','=','inventory')])
            if ubicacion_desecho_ids:
                move_obj.write(cr, uid, move_ids, {'location_dest_id':ubicacion_desecho_ids[0], 'state':'done'})
                self.escribir_objeto_distinta_compania(cr, uid, picking_obj.browse(cr, uid, existe_picking[0]), {'state':'done'})
        if estado == 'cancelado':
            move_obj.write(cr, uid, move_ids, {'state':'cancel'})
            self.escribir_objeto_distinta_compania(cr, uid, picking_obj.browse(cr, uid, existe_picking[0]), {'state':'cancel'})
        move_ids = []
        return True

    def destino_clientes(self, cr, uid, picking):
        location_obj = self.pool.get('stock.location')
        res = False
        origen, destino = self.obtener_ubicacion_origen_y_destino(cr, uid, picking)
        if location_obj.browse(cr, SUPERUSER_ID, destino).usage == 'customer':
            res = True
        return res

    def movimientos_cajas(self, cr, uid, ids, vals=None):
        caja_obj = self.pool.get('stock.caja.transporte')
        estado = vals.get('state', False)
        comp_estado = [
            'despachado',
            'perdido',
            'cancelado',
            'entregado'
        ]
        if estado:
            if estado in comp_estado:
                for ot in self.browse(cr, uid, ids):
                    if ot.ot_type == 'hija' and ot.picking_id and ot.cajas_ids:
                        cliente_externo = self.destino_clientes(cr, uid, ot.picking_id)
                        cajas = [c.id for c in ot.cajas_ids]
                        usan_producto = False
                        for caja in caja_obj.browse(cr, uid, cajas):
                            if caja.product_id:
                                usan_producto = True
                        if usan_producto:
                            #Crear picking asociado al picking_id
                            #y el movimieto en estado esperando o reservado.
                            self.picking_cajas(cr, uid, cajas, ot.picking_id, caja_obj, estado)
        return True

    def ejecuta_pre_write(self, cr, uid, ids, vals, context=None):
        return True

    def ejecuta_post_write(self, cr, uid, ids, vals, context=None):
        self.todos_entregados(cr, uid, ids)
        self.movimientos_cajas(cr, uid, ids, vals=vals)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        self.ejecuta_pre_write(cr, uid, ids, vals, context=context)
        res = super(stock_orden_transporte, self).write(cr, uid, ids, vals,context=context)
        self.ejecuta_post_write(cr, uid, ids, vals, context=context)
        return res



stock_orden_transporte()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def entregado_met(self, cr, uid, ids, context=None):
        res = super(stock_picking, self).entregado_met(cr, uid, ids, context=context)
        for pick in self.browse(cr, uid, ids):
            if pick.orden_transporte_id:
                self.pool.get('stock.orden.transporte').write(cr, uid, [pick.orden_transporte_id.id], {'state':'entregado'})
        return res

    _columns = {
        'orden_transporte_id': fields.many2one('stock.orden.transporte', 'Orden de Transporte', readonly=True, track_visibility='onchange'),
        'cajas_ids': fields.many2many('stock.caja.transporte', 'caja_pick_rel','pick_id','caja_id', 'Cajas'),
    }

    def obtener_id_compania(self, cr, uid, picking):
        compania_destino_comun = False
        pick_id = picking.id
        pick_obj = self.pool.get('stock.picking')
        picking = pick_obj.browse(cr, SUPERUSER_ID, pick_id)
        mismo_destino = False
        for move in picking.move_lines:
            if not mismo_destino:
                mismo_destino = move.location_dest_id.id
                if move.location_dest_id.company_id:
                    compania_destino_comun = move.location_dest_id.company_id.id
            else:
                if move.location_dest_id.id != mismo_destino:
                    compania_destino_comun = False
        return compania_destino_comun

    def crear_ot_hija(self, cr, uid, picking):
        if not picking.cajas_ids:
            raise osv.except_osv('Error!', 'Primero debe ingresar las cajas, luego generar la OT.')
            return False
        secuencia_ot = self.pool.get('ir.sequence').get(cr, uid, 'traza.orden.transporte')
        ot_hija_name = secuencia_ot
        ot_hija_name = ot_hija_name + 'OTH'
        compania_id = self.obtener_id_compania(cr, uid, picking)
        res = False
        ot_obj = self.pool.get('stock.orden.transporte')
        vals_ot = dict()
        vals_ot['name'] = ot_hija_name
        vals_ot['picking_id'] = picking.id
        vals_ot['state'] = 'esperando'
        vals_ot['ot_type'] = 'hija'
        vals_ot['company_id'] = compania_id
        lista_cajas_ids = []
        for c in picking.cajas_ids:
            lista_cajas_ids.append((4,c.id))
        if lista_cajas_ids:
            vals_ot['cajas_ids'] = lista_cajas_ids
        ot_hija_id = ot_obj.create(cr, uid, vals_ot)
        if ot_hija_id:
            self.write(cr, uid, [picking.id], {'orden_transporte_id': int(ot_hija_id)})
            res = True
        return res

    def asignar_ot_picking(self, cr, uid, ids, context=None):
        res = True
        for picking in self.browse(cr, uid, ids):
            self.crear_ot_hija(cr, uid, picking)
        return res

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"

    _columns = {
        'orden_transporte_id': fields.many2one('stock.orden.transporte', 'Orden de Transporte', readonly=True, track_visibility='onchange'),
        'cajas_ids': fields.many2many('stock.caja.transporte', 'caja_pick_rel','pick_id','caja_id', 'Cajas'),
    }

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"

    _columns = {
        'orden_transporte_id': fields.many2one('stock.orden.transporte', 'Orden de Transporte', readonly=True, track_visibility='onchange'),
        'cajas_ids': fields.many2many('stock.caja.transporte', 'caja_pick_rel','pick_id','caja_id', 'Cajas'),
    }

    def asignar_ot_picking(self, cr, uid, ids, context=None):
        res = self.pool.get('stock.picking').asignar_ot_picking(cr, uid, ids, context=context)
        return res
