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
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging

#------------------------------------------
# Registro cambios Posicion por Ubicacion
#------------------------------------------
class registro_cambios_posicion_por_ubicacion(osv.Model):
    _name = "registro.cambios.posicion.por.ubicacion"
    _order = "id desc"

    _columns = {
        'antes': fields.text('Antes', readonly=True),
        'despues': fields.text('Despues', readonly=True),
        'ppu_id' : fields.many2one('posicion.por.ubicacion', 'Posicion', ondelete='set null', select=1, readonly=True),
        'ppu_linea_id' : fields.many2one('posicion.por.ubicacion.linea', 'Posicion (Linea)', ondelete='set null', select=1, readonly=True),
        'product_id' : fields.many2one('product.product', 'Producto', ondelete='set null', select=1),
        'create_uid': fields.many2one('res.users', 'Creador', readonly=True),
        'write_uid': fields.many2one('res.users', 'Modificador', readonly=True),
        'create_date': fields.datetime('Creacion', readonly=True),
        'write_date': fields.datetime('Modificacion', readonly=True),
    }

#------------------------------------------
# Posicion por Ubicacion
#------------------------------------------
class posicion_por_ubicacion(osv.Model):
    _name = "posicion.por.ubicacion"
    _order = "id asc"

    def _get_company_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = user.company_id and user.company_id.id or False
        return res

    def _posicion_disponible(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict()
        for ppu in self.browse(cr, uid, ids):
            res[ppu.id] = True
            if ppu.posiciones_lineas_ids:
                res[ppu.id] = False
        return res

    def _salida_intermedio_entrada(self, cr, uid, ids, fieldnames, args, context=None):

        res = dict()

        for ppu in self.browse(cr, uid, ids):
            res[ppu.id] = {
                'entrada': False,
                'salida': False,
                'intermedio': False,
            }

            intermedio = False
            entrada = False
            salida = False

            if ppu.ppu_desde_id and ppu.ppu_hasta_ids:
                intermedio = True
            if ppu.ppu_hasta_ids and not intermedio:
                entrada = True
            if ppu.ppu_desde_id and not intermedio:
                salida = True
            if not intermedio and not salida and not entrada:
                if ppu.posiciones_lineas_ids:
                    salida = True

            res[ppu.id]['intermedio'] = intermedio
            res[ppu.id]['entrada'] = entrada
            res[ppu.id]['salida'] = salida

        return res

    _columns = {
        'name': fields.char('Posicion', size=32, required=True),
        'posiciones_lineas_ids' : fields.one2many('posicion.por.ubicacion.linea', 'ppu_id','Productos'),
        'location_id' : fields.many2one('stock.location', 'Ubicacion', ondelete='set null', select=1, required=True),
        'ppu_desde_id' : fields.many2one('posicion.por.ubicacion', 'Posicion Desde', ondelete='set null', select=1, domain=[('salida','=',False)]),
        'ppu_hasta_ids' : fields.one2many('posicion.por.ubicacion', 'ppu_desde_id','Posiciones Hasta'),
        'tipo_almacenamiento': fields.selection([('rack', 'Rack'),('estante', 'Estante'),('pasillo', 'Pasillo')], 'Tipo Almacenamiento', required=True, select=1),
        'state': fields.selection([('esperando','Esperando'),('retraso','Retraso'),('hecho','Hecho'),('cancelado','Cancelado')], 'Estado', readonly=True, select=True),
        'salida': fields.function(_salida_intermedio_entrada, type='boolean', string='Salida', multi='tipo_posicion', store=True),
        'entrada': fields.function(_salida_intermedio_entrada, type='boolean', string='Entrada', multi='tipo_posicion', store=True),
        'intermedio': fields.function(_salida_intermedio_entrada, type='boolean', string='Intermedio', multi='tipo_posicion', store=True),
        'company_id': fields.many2one('res.company', 'Compania', select=1),
        'active': fields.boolean('Activo'),
        'flujo': fields.boolean('Maneja Flujo'),
        'vacio': fields.function(_posicion_disponible, type='boolean', string='Disponible', multi=False, store=True),
        'create_uid': fields.many2one('res.users', 'Creador', readonly=True),
        'write_uid': fields.many2one('res.users', 'Modificador', readonly=True),
        'create_date': fields.datetime('Fecha creacion', readonly=True),
        'write_date': fields.datetime('Fecha Modificacion', readonly=True),
        'last_check_date': fields.datetime('Fecha ultima revision', readonly=True),
        'last_check_uid': fields.many2one('res.users', 'Revisado por', readonly=True),
    }

    _defaults = {
        'state': 'hecho',
        'vacio': True,
        'active': True,
        'flujo': False,
        'company_id': lambda self, cr, uid, c: self._get_company_id(cr, uid, context=c),
    }

    def actualiza_lineas(self, cr, uid, ids):
        lpu_obj = self.pool.get('posicion.por.ubicacion.linea')

        for pu in self.browse(cr, uid, ids):
            lineas_ids = [lpu.id for lpu in pu.posiciones_lineas_ids]
            if lineas_ids:

                vals_lpu = dict()
                vals_lpu['name'] = pu.name
                vals_lpu['entrada'] = False
                vals_lpu['intermedio'] = False
                vals_lpu['salida'] = False

                vals_lpu['location_id'] = pu.location_id.id
                vals_lpu['flujo'] = pu.flujo
                vals_lpu['active'] = pu.active
                if pu.company_id:
                    vals_lpu['company_id'] = pu.company_id.id

                if pu.entrada:
                    vals_lpu['entrada'] = True
                if pu.intermedio:
                    vals_lpu['intermedio'] = True
                if pu.salida:
                    vals_lpu['salida'] = True

                lpu_obj.write(cr, uid, lineas_ids, vals_lpu)

        return True

    def chequea_productos_repetidos(self, cr, uid, ids):
        for pu in self.browse(cr, uid, ids):
            lista_productos = []
            for linea in pu.posiciones_lineas_ids:
                if linea.product_id.id not in lista_productos:
                    lista_productos.append(linea.product_id.id)
                else:
                    raise osv.except_osv('Error','No puede repetir productos. (%s).'%linea.product_id.name)
        return True

    def crea_registro_cambios(self, cr, uid, ids, vals):
        registro_obj = self.pool.get('registro.cambios.posicion.por.ubicacion')
        lista_campos = vals.keys()
        for pu in self.read(cr, uid, ids, lista_campos):
            pu_id = pu.get('id',False)
            vals_reg = dict()
            vals_reg['antes'] = 'POSICION ' + str(pu)
            vals_reg['despues'] = str(vals)
            if pu_id:
                vals_reg['ppu_id'] = pu_id
            registro_obj.create(cr, uid, vals_reg)
        return True

    def ejecuta_pre_write(self, cr, uid, ids, vals, context=None):
        #self.crea_registro_cambios(cr, uid, ids, vals)
        return True

    def ejecuta_post_write(self, cr, uid, ids, vals, context=None):
        self.actualiza_lineas(cr, uid, ids)
        self.chequea_productos_repetidos(cr, uid, ids)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        self.ejecuta_pre_write(cr, uid, ids, vals, context=context)
        res = super(posicion_por_ubicacion, self).write(cr, uid, ids, vals, context=context)
        self.ejecuta_post_write(cr, uid, ids, vals, context=context)
        return res

#------------------------------------------
# Posicion por Ubicacion Linea
#------------------------------------------
class posicion_por_ubicacion_linea(osv.Model):
    _name = "posicion.por.ubicacion.linea"
    _order = "ppu_id asc, product_id"

    def _get_company_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = user.company_id and user.company_id.id or False
        return res

    _columns = {
        'name': fields.char('Nombre', size=32),
        'product_id' : fields.many2one('product.product', 'Producto', ondelete='set null', select=1, required=True, domain=[('type', '<>', 'service')]),
        'location_id' : fields.many2one('stock.location', 'Ubicacion', ondelete='set null', select=1),
        'cantidad': fields.float('Cantidad'),
        'cantidad_entrante': fields.float('Cantidad Entrante'),
        'cantidad_saliente': fields.float('Cantidad Saliente'),
        'capacidad': fields.integer('Capacidad'),
        'ppu_id' : fields.many2one('posicion.por.ubicacion', 'Posicion', ondelete='set null', select=1),
        'state': fields.selection([('esperando','Esperando'),('retraso','Retraso'),('hecho','Hecho'),('cancelado','Cancelado')], 'Estado', readonly=True, select=True),
        'salida': fields.boolean('Salida'),
        'entrada': fields.boolean('Entrada'),
        'intermedio': fields.boolean('Intermedio'),
        'company_id': fields.many2one('res.company', 'Compania', select=1),
        'active': fields.boolean('Activo'),
        'flujo': fields.boolean('Maneja Flujo'),
    }

    _defaults = {
        'state': 'hecho',
        'active': True,
        'flujo': False,
        'company_id': lambda self, cr, uid, c: self._get_company_id(cr, uid, context=c),
    }

    def crea_registro_cambios_linea(self, cr, uid, ids, vals):
        registro_obj = self.pool.get('registro.cambios.posicion.por.ubicacion')
        lista_campos = vals.keys()
        if 'ppu_id' not in lista_campos:
            lista_campos += ['ppu_id']
        product_id = vals.get('product_id', False)
        for pul in self.read(cr, uid, ids, lista_campos):
            ppu_id = pul.get('ppu_id', False)
            pu_id = pul.get('id', False)
            vals_reg = dict()
            vals_reg['antes'] = 'LINEA POSICION ' + str(pul)
            vals_reg['despues'] = str(vals)
            vals_reg['ppu_id'] = ppu_id[0]
            vals_reg['ppu_linea_id'] = pu_id
            if product_id:
                vals_reg['product_id'] = product_id
            registro_obj.create(cr, uid, vals_reg)
        return True

    def ejecuta_pre_write_linea(self, cr, uid, ids, vals, context=None):
        #self.crea_registro_cambios_linea(cr, uid, ids, vals)
        return True

    def ejecuta_post_write_linea(self, cr, uid, ids, vals, context=None):
        return True

    def write(self, cr, uid, ids, vals, context=None):
        self.ejecuta_pre_write_linea(cr, uid, ids, vals, context=context)
        res = super(posicion_por_ubicacion_linea, self).write(cr, uid, ids, vals, context=context)
        self.ejecuta_post_write_linea(cr, uid, ids, vals, context=context)
        return res

#------------------------------------------
# Flujo entre posiciones
#------------------------------------------
class flujo_entre_posiciones(osv.Model):
    _name = "flujo.entre.posiciones"
    _inherit = ['mail.thread']
    _description = "Flujo entre Posiciones"
    _order = "id desc"


    def _get_company_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = user.company_id and user.company_id.id or False
        return res

    def arregla_flujos(self, cr, uid, ids, stock_move_obj):
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        posicion_linea_obj = self.pool.get('posicion.por.ubicacion.linea')
        cantidad_total = 0.0
        posicion_desde = False
        posicion_hasta = False
        linea_origen = False
        linea_destino = False
        for flujo in self.browse(cr, uid, ids):
            cantidad_total += flujo.cantidad
            if not posicion_desde:
                posicion_desde = flujo.ppu_desde_id
            if not posicion_hasta:
                posicion_hasta = flujo.ppu_hasta_id
            if not linea_origen:
                linea_origen = flujo.linea_origen_id
            if not linea_destino:
                linea_destino = flujo.linea_destino_id
        cantidad_total += stock_move_obj.product_qty
        self.unlink(cr, SUPERUSER_ID, ids)

        #### Dif. a reponer ####
        capacidad = 0.0
        diferencia_a_reponer = 0.0
        if linea_destino.capacidad:
            capacidad = float(linea_destino.capacidad)
        cantidad_saliente = 0.0
        if linea_destino.cantidad_saliente:
            cantidad_saliente = linea_destino.cantidad_saliente
        linea_cantidad = 0.0
        if linea_destino.cantidad:
            linea_cantidad = linea_destino.cantidad
        if cantidad_saliente:
            cantidad_final = linea_cantidad - cantidad_saliente
        else:
            if not linea_cantidad:
                if capacidad:
                    cantidad_final = capacidad
                else:
                    cantidad_final = cantidad_total
            else:
                cantidad_final = linea_cantidad
        if (cantidad_final > 0.0) and (capacidad > cantidad_final):
            diferencia_a_reponer = capacidad - cantidad_final
        if (cantidad_final > 0.0) and (capacidad == cantidad_final):
            diferencia_a_reponer = cantidad_final
        if cantidad_final < 0.0:
            diferencia_a_reponer = capacidad or cantidad_total
        if diferencia_a_reponer > 0.0:
            cantidad_total = diferencia_a_reponer
        #### Dif. a reponer ####

        vals_crear_flujo = dict()
        vals_crear_flujo['name'] = posicion_desde.name + ' ' + posicion_hasta.name + ' ' + stock_move_obj.product_id.name
        vals_crear_flujo['ppu_desde_id'] = posicion_desde.id
        vals_crear_flujo['ppu_hasta_id'] = posicion_hasta.id
        vals_crear_flujo['linea_origen_id'] = linea_origen.id
        vals_crear_flujo['linea_destino_id'] = linea_destino.id
        vals_crear_flujo['product_id'] = stock_move_obj.product_id.id
        vals_crear_flujo['location_id'] = stock_move_obj.location_id.id
        vals_crear_flujo['cantidad'] = cantidad_total
        self.create(cr, uid, vals_crear_flujo)
        posiciones_ids = [posicion_desde.id, posicion_hasta.id]
        posicion_obj.write(cr, uid, posiciones_ids, {'state':'esperando'})
        lineas_ids = [linea_origen.id, linea_destino.id]
        posicion_linea_obj.write(cr, uid, lineas_ids, {'state':'esperando'})
        posicion_linea_obj.write(cr, uid, [linea_origen.id], {'cantidad_saliente':cantidad_total})
        return True

    def procesa_flujo(self, cr, uid, ids, context=None):
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        posicion_linea_obj = self.pool.get('posicion.por.ubicacion.linea')
        for flujo in self.browse(cr, uid, ids):
            cantidad = flujo.cantidad
            self.write(cr, uid, [flujo.id], {'state':'hecho'})
            posicion_linea_obj.write(cr, uid, [flujo.linea_origen_id.id], {'cantidad':flujo.linea_origen_id.cantidad - cantidad,'state':'hecho','cantidad_saliente':0.0})
            posicion_linea_obj.write(cr, uid, [flujo.linea_destino_id.id], {'cantidad':flujo.linea_destino_id.cantidad + cantidad,'state':'hecho'})
            lista_posiciones = [flujo.ppu_desde_id.id, flujo.ppu_hasta_id.id]
            posicion_obj.write(cr, uid, lista_posiciones, {'state':'hecho'})
        return True

    def cancela_flujo(self, cr, uid, ids, context=None):
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        posicion_linea_obj = self.pool.get('posicion.por.ubicacion.linea')
        for flujo in self.browse(cr, uid, ids):
            lista_posiciones = [flujo.ppu_desde_id.id, flujo.ppu_hasta_id.id]
            posicion_obj.write(cr, uid, lista_posiciones, {'state':'cancelado'})
            self.write(cr, uid, [flujo.id], {'state':'cancelado'})
            lista_lineas_posiciones = [flujo.linea_origen_id.id, flujo.linea_destino_id.id]
            posicion_linea_obj.write(cr, uid, lista_lineas_posiciones, {'state':'cancelado','cantidad_saliente':0.0})
        return True

    def _cron_retraso(self, cr, uid, ids=False, context=None):
        logger = logging.getLogger('log._cron_retraso')
        logger.warn('################# SE EJECUTA CRON RETRASO ####################')
        ahora = datetime.now()
        fecha_hora_desde = ahora - relativedelta(days=2)
        fecha_hora_hasta = ahora - relativedelta(hours=10)
        fecha_hora_desde = fecha_hora_desde.strftime('%Y-%m-%d %H:%M:%S')
        fecha_hora_hasta = fecha_hora_hasta.strftime('%Y-%m-%d %H:%M:%S')
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        posicion_linea_obj = self.pool.get('posicion.por.ubicacion.linea')
        new_ids = self.search(cr, uid, [('create_date','>=',fecha_hora_desde),('create_date','<=',fecha_hora_hasta),('state','=','pendiente')])
        if not new_ids:
            logger.warn('if not new_ids')
            return True
        lista_posiciones_ids = []
        lista_lineas_posiciones_ids = []
        for flujo in self.browse(cr, uid, new_ids):
            lista_posiciones_ids.append(flujo.ppu_desde_id.id)
            lista_posiciones_ids.append(flujo.ppu_hasta_id.id)
            lista_lineas_posiciones_ids.append(flujo.linea_origen_id.id)
            lista_lineas_posiciones_ids.append(flujo.linea_destino_id.id)
        self.write(cr, uid, new_ids, {'state':'retraso'})
        posicion_obj.write(cr, uid, lista_posiciones_ids, {'state':'retraso'})
        posicion_linea_obj.write(cr, uid, lista_lineas_posiciones_ids, {'state':'retraso'})
        lista_posiciones_ids = []
        logger.warn('################# FINALIZA CRON RETRASO ####################')
        return True

    _columns = {
        'name': fields.char('Flujo', size=64),
        'plazo': fields.integer('Plazo (dias)', help="Numero de dias para ejecutar los flujos"),
        'ppu_desde_id' : fields.many2one('posicion.por.ubicacion', 'Desde', ondelete='set null', select=1),
        'ppu_hasta_id' : fields.many2one('posicion.por.ubicacion', 'Hasta', ondelete='set null', select=1),
        'linea_origen_id': fields.many2one('posicion.por.ubicacion.linea', 'Linea Desde', ondelete='set null', select=1, required=True),
        'linea_destino_id': fields.many2one('posicion.por.ubicacion.linea', 'Linea Hasta', ondelete='set null', select=1, required=True),
        'product_id' : fields.many2one('product.product', 'Producto', ondelete='set null', select=1, readonly=True),
        'cantidad': fields.float('Cantidad', required=True, states={'hecho': [('readonly', True)], 'cancelado': [('readonly', True)]}, track_visibility='onchange'),
        'location_id' : fields.many2one('stock.location', 'Ubicacion', ondelete='set null', select=1, required=True),
        'state': fields.selection([('pendiente','Pendiente'),('retraso','Retraso'),('hecho','Hecho'),('cancelado','Cancelado')], 'Estado', readonly=True, select=True, track_visibility='onchange'),
        'company_id': fields.many2one('res.company', 'Compania', select=1),
        'create_uid': fields.many2one('res.users', 'Creador', readonly=True),
        'write_uid': fields.many2one('res.users', 'Modificador', readonly=True),
        'create_date': fields.datetime('Fecha creacion', readonly=True),
        'write_date': fields.datetime('Fecha Modificacion', readonly=True),
    }

    _defaults = {
        'plazo': 1,
        'state': 'pendiente',
        'company_id': lambda self, cr, uid, c: self._get_company_id(cr, uid, context=c),
    }

#------------------------------------------
# Stock Move
#------------------------------------------
class stock_move(osv.Model):
    _inherit = "stock.move"

    def chequea_compania(self, cr, uid, move):

        res = False
        comp_usuario = False
        comp_movimiento = False
        comp_albaran = False

        comp_user = self.pool.get('res.users').browse(cr, uid, uid).company_id

        if comp_user:
            comp_usuario = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        if move.company_id:
            comp_movimiento = move.company_id.id
        if move.picking_id.company_id:
            comp_albaran = move.picking_id.company_id.id

        if comp_usuario == comp_movimiento == comp_albaran:
            if comp_usuario:
                res = comp_usuario

        return res

    def crear_flujo_entre_lineas(self, cr, uid, move, linea, poslin_obj):
        flujo_obj = self.pool.get('flujo.entre.posiciones')
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        if linea.ppu_id.ppu_desde_id:
            linea_desde_obj = False
            for linea_desde in linea.ppu_id.ppu_desde_id.posiciones_lineas_ids:
                if linea_desde.product_id.id == linea.product_id.id:
                    linea_desde_obj = linea_desde
            if linea_desde_obj:
                #Busca Flujo, si no hay similares lo crea.
                criterio_flujo = []
                criterio_flujo.append(('product_id','=',linea.product_id.id))
                criterio_flujo.append(('linea_origen_id','=',linea_desde_obj.id))
                criterio_flujo.append(('linea_destino_id','=',linea.id))
                criterio_flujo.append(('state','not in',('hecho','cancelado')))
                flujos_ids =flujo_obj.search(cr, uid, criterio_flujo)
                if flujos_ids:
                    flujo_obj.arregla_flujos(cr, uid, flujos_ids, move)
                else:
                    cantidad = move.product_qty

                    #### Dif. a reponer ####
                    capacidad = 0.0
                    diferencia_a_reponer = 0.0
                    if linea.capacidad:
                        capacidad = float(linea.capacidad)
                    cantidad_saliente = 0.0
                    if linea.cantidad_saliente:
                        cantidad_saliente = linea.cantidad_saliente
                    linea_cantidad = 0.0
                    if linea.cantidad:
                        linea_cantidad = linea.cantidad
                    if cantidad_saliente:
                        cantidad_final = linea_cantidad - cantidad_saliente
                    else:
                        if not linea_cantidad:
                            if capacidad:
                                cantidad_final = capacidad
                            else:
                                cantidad_final = cantidad
                        else:
                            cantidad_final = linea_cantidad
                    if (cantidad_final > 0.0) and (capacidad > cantidad_final):
                        diferencia_a_reponer = capacidad - cantidad_final
                    if (cantidad_final > 0.0) and (capacidad == cantidad_final):
                        diferencia_a_reponer = cantidad_final
                    if cantidad_final < 0.0:
                        diferencia_a_reponer = capacidad or cantidad
                    if diferencia_a_reponer > 0.0:
                        cantidad = diferencia_a_reponer
                    #### Dif. a reponer ####

                    if cantidad > linea_desde_obj.cantidad:
                        cantidad = linea_desde_obj.cantidad

                    vals_creacion_flujo = dict()
                    vals_creacion_flujo['name'] = str(linea_desde_obj.ppu_id.name) + ' ' + str(linea.ppu_id.name) + ' ' + str(linea.product_id.name)
                    vals_creacion_flujo['product_id'] = linea.product_id.id
                    vals_creacion_flujo['ppu_desde_id'] = linea_desde_obj.ppu_id.id
                    vals_creacion_flujo['ppu_hasta_id'] = linea.ppu_id.id
                    vals_creacion_flujo['linea_origen_id'] = linea_desde_obj.id
                    vals_creacion_flujo['linea_destino_id'] = linea.id
                    vals_creacion_flujo['cantidad'] = cantidad
                    vals_creacion_flujo['location_id'] = move.location_id.id
                    vals_creacion_flujo['state'] = 'pendiente'
                    vals_creacion_flujo['company_id'] = move.company_id.id
                    flujo_obj.create(cr, uid, vals_creacion_flujo)
                    poslin_obj.write(cr, uid, [linea_desde_obj.id], {'cantidad_saliente':cantidad})

        return True

    def crear_por_linea_mientras_haya_origen(self, cr, uid, move, linea_id, poslin_obj):
        
        linea = poslin_obj.browse(cr, uid, linea_id)
        cantidad = move.product_qty
        diferencia = 0.0
        total_a_restar = cantidad
        while linea:

            cantidad_a_restar = total_a_restar
            if total_a_restar < 0:
                cantidad_a_restar = 0.0

            if diferencia:
                cantidad_a_restar = diferencia

            if cantidad_a_restar > linea.cantidad:
                diferencia = cantidad_a_restar - linea.cantidad
                cantidad_a_restar = linea.cantidad
            else:
                diferencia = 0.0
            cantidad_final = linea.cantidad - cantidad_a_restar
            total_a_restar -= cantidad_a_restar
            poslin_obj.write(cr, uid, [linea.id], {'cantidad':cantidad_final})

            linea_actualizada = poslin_obj.browse(cr, uid, linea.id)
            self.crear_flujo_entre_lineas(cr, uid, move, linea_actualizada, poslin_obj)

            if not linea.ppu_id.ppu_desde_id:
                linea = False
            else:
                linea_temp = False
                for linea_desde in linea.ppu_id.ppu_desde_id.posiciones_lineas_ids:
                    if linea_desde.product_id.id == linea.product_id.id:
                        linea_temp = linea_desde
                linea = linea_temp

        return True

    def crear_flujo(self, cr, uid, ids, context=None):
        posicion_linea_obj = self.pool.get('posicion.por.ubicacion.linea')
        for move in self.browse(cr, uid, ids):
            company_id = self.chequea_compania(cr, uid, move)
            if company_id:
                criterio_busqueda = []
                criterio_busqueda.append(('product_id','=',move.product_id.id))
                criterio_busqueda.append(('location_id','=',move.location_id.id))
                criterio_busqueda.append(('salida','=',True))
                criterio_busqueda.append(('flujo','=',True))
                linea_salida_ids = posicion_linea_obj.search(cr, uid, criterio_busqueda)
                if linea_salida_ids and len(linea_salida_ids) == 1:
                    self.crear_por_linea_mientras_haya_origen(cr, uid, move, linea_salida_ids[0], posicion_linea_obj)
        return True

    def action_done(self, cr, uid, ids, context=None):
        res = super(stock_move, self).action_done(cr, uid, ids, context=context)
        self.crear_flujo(cr, uid, ids)
        return res
