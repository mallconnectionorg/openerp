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
import string
import logging
import base64
import cStringIO
from datetime import datetime

#------------------------------------------
# Posicion por Ubicacion Wizard
#------------------------------------------
class posicion_por_ubicacion_wizard(osv.osv_memory):
    _name = "posicion.por.ubicacion.wizard"

    def comprueba_inicio_final_rpe(self, cr, uid, ppuw):
        res = dict()
        res['res'] = True
        res['cantidad'] = 0
        res['rpe'] = False
        mismo_tipo = True
        try:
            inicio = float(ppuw.inicio_rack_pasillo_estante)
        except ValueError:
            inicio = str(ppuw.inicio_rack_pasillo_estante.upper())
        try:
            final = float(ppuw.final_rack_pasillo_estante)
        except ValueError:
            final = str(ppuw.final_rack_pasillo_estante.upper())
        tipo_inicio = type(inicio)
        tipo_final = type(final)
        if tipo_inicio != tipo_final:
            res['res'] = False
            mismo_tipo = False
        if tipo_inicio == type('A') and mismo_tipo:
            #Incrementar letra hasta letra final
            alfabeto = string.ascii_uppercase
            comienzo = False
            lista_letras = []
            for letra in alfabeto:
                if inicio == letra:
                    comienzo = True
                if comienzo:
                    lista_letras.append(letra)
                if final == letra:
                    break
            res['cantidad'] = len(lista_letras)
            res['rpe'] = lista_letras
        
        if tipo_inicio == type(float(1)) and mismo_tipo:
            res['cantidad'] = int(final - inicio + 1)
            lista_numeros = []
            inicio = int(inicio)
            final = int(final)
            for i in range(inicio, final + 1):
                lista_numeros.append(str(i))
            res['rpe'] = lista_numeros
        if not res['rpe'] or not res['cantidad']:
            res['res'] = False
        res['cantidad_posiciones'] = str(res['cantidad'] * ppuw.cantidad_filas * ppuw.cantidad_columnas) or 0
        return res

    def crear_ejemplo(self, cr, uid, ppuw):
        cantidad_rpe = '0'
        rpe = 'A'
        columna = '1'
        fila = '1'
        if ppuw.rack_pasillo_estante == 'numerico':
            rpe = '1'
        if ppuw.columna == 'alfabetico':
            columna = 'A'
        if ppuw.fila == 'alfabetico':
            fila = 'A'
        inicio_final_rpe = self.comprueba_inicio_final_rpe(cr, uid, ppuw)
        if inicio_final_rpe['res']:
            cantidad_rpe = inicio_final_rpe['cantidad']
            cantidad_posiciones = inicio_final_rpe['cantidad_posiciones']
        ejemplo = rpe + '-' + columna + '-' + fila
        write_vals = dict()
        write_vals['ejemplo'] = ejemplo
        write_vals['cantidad_rack_pasillo_estante'] = cantidad_rpe
        write_vals['cantidad_posiciones'] = cantidad_posiciones
        self.write(cr, uid, [ppuw.id], write_vals)
        return True

    def ver_ejemplo(self, cr, uid, ids, context=None):
        for ppuw in self.browse(cr, uid, ids):
            self.crear_ejemplo(cr, uid, ppuw)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'posicion.por.ubicacion.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': ppuw.id,
                'views': [(False, 'form')],
                'target': 'new',
                }

    def lista_letras(self, cr, uid, cantidad):
        alfabeto = string.ascii_uppercase
        res = []
        if cantidad > 676:
            return res
        prefijo = ''
        salir = False
        contador = 0
        for i in range(0,26):
            for a in range(0,26):
                res.append(prefijo + alfabeto[a])
                contador += 1
                if contador >= cantidad:
                    salir = True
                if salir:
                    break
            prefijo = alfabeto[i]
            if salir:
                break

        return res

            

    def cal_filas_columnas(self, cr, uid, ppuw):
        res = dict()
        res['filas'] = False
        res['columnas'] = False
        cantidad_filas = ppuw.cantidad_filas
        cantidad_columnas = ppuw.cantidad_columnas
        fila_tipo = ppuw.fila
        columna_tipo = ppuw.columna
        if fila_tipo == 'numerico':
            lista_filas = []
            for i in range(1, cantidad_filas + 1):
                lista_filas.append(str(i))
            res['filas'] = lista_filas
        else:
            res['filas'] = self.lista_letras(cr, uid, cantidad_filas)
        if columna_tipo == 'numerico':
            lista_columnas = []
            for j in range(1, cantidad_columnas + 1):
                lista_columnas.append(str(j))
            res['columnas'] = lista_columnas
        else:
            res['columnas'] = self.lista_letras(cr, uid, cantidad_columnas)
        return res

    def crear_posiciones(self, cr, uid, ids, context=None):
        for ppuw in self.browse(cr, uid, ids):
            inicio_final_rpe = self.comprueba_inicio_final_rpe(cr, uid, ppuw)
            if not inicio_final_rpe['res']:
                return True
            rpe = inicio_final_rpe['rpe']
            columnas = self.cal_filas_columnas(cr, uid, ppuw)['columnas']
            filas = self.cal_filas_columnas(cr, uid, ppuw)['filas']
            lista_posciones = []
            for elem in rpe:
                for col in columnas:
                    for fila in filas:
                        pos_texto = elem + '-' + col + '-' + fila
                        lista_posciones.append(pos_texto)
            for lp in lista_posciones:
                create_vals = dict()
                create_vals['location_id'] = ppuw.location_id.id
                create_vals['tipo_almacenamiento'] = ppuw.tipo_ordenamiento
                create_vals['active'] = ppuw.active
                create_vals['flujo'] = ppuw.flujo
                create_vals['name'] = lp
                if ppuw.company_id:
                    create_vals['company_id'] = ppuw.company_id.id
                self.pool.get('posicion.por.ubicacion').create(cr, uid, create_vals)
                        
        return True

    def _get_company_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = user.company_id and user.company_id.id or False
        return res

    _columns = {
        'name': fields.char('Name', size=32),
        'location_id' : fields.many2one('stock.location', 'Ubicacion', ondelete='set null', select=1, required=True, domain="[('company_id','=',company_id)]"),
        'tipo_ordenamiento': fields.selection([('rack','Rack'),('estante','Estante'),('pasillo','Pasillo')], 'Tipo Ordenamiento', required=True, select=1,),
        'company_id': fields.many2one('res.company', 'Compania', select=1),
        'active': fields.boolean('Activo'),
        'flujo': fields.boolean('Manejan Flujo'),
        'rack_pasillo_estante': fields.selection([('numerico','Numerico'),('alfabetico','Alfabetico')], 'Tipo identificador Rack/Pasillo/Estante', required=True),
        'fila': fields.selection([('numerico','Numerico'),('alfabetico','Alfabetico')], 'Tipo identificador Fila', required=True),
        'columna': fields.selection([('numerico','Numerico'),('alfabetico','Alfabetico')], 'Tipo identificador Columna', required=True),
        'inicio_rack_pasillo_estante': fields.char('Inicio Rack/Pasillo/Estante', size=8, required=True),
        'final_rack_pasillo_estante': fields.char('Final Rack/Pasillo/Estante', size=8, required=True),
        'cantidad_filas': fields.integer('Cantidad de Filas', required=True),
        'cantidad_columnas': fields.integer('Cantidad de Columnas por Rack/Pasillo/Estante', required=True),
        'ejemplo': fields.char('Ejemplo', size=32, readonly=True),
        'cantidad_rack_pasillo_estante': fields.char('Cantidad Rack/Pasillo/Estante', size=8, readonly=True),
        'cantidad_posiciones': fields.char('Cantidad de Posiciones', size=8, readonly=True)
    }

    _defaults = {
        'active': True,
        'flujo': False,
        'company_id': lambda self, cr, uid, c: self._get_company_id(cr, uid, context=c),
    }

posicion_por_ubicacion_wizard()
#------------------------------------------
# Revisa Posicion por Ubicacion Wizard
#------------------------------------------
class revisa_posicion_por_ubicacion_wizard(osv.osv_memory):
    _name = "revisa.posicion.por.ubicacion.wizard"

    def _get_company_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = user.company_id and user.company_id.id or False
        return res

    _columns = {
        'name': fields.char('Revision', size=32),
        'encontradas': fields.integer('Se encontraron ', readonly=True),
        'location_id' : fields.many2one('stock.location', 'Ubicacion', required=True, domain="[('company_id','=',company_id)]"),
        'tipo_almacenamiento': fields.selection([('rack', 'Rack'),('estante', 'Estante'),('pasillo', 'Pasillo'),('todas', 'Todas')], 'Por tipo de almacenamiento', required=True),
        'estado': fields.selection([('esperando','Esperando'),('retraso','Retraso'),('hecho','Hecho'),('cancelado','Cancelado'),('todas', 'Todas')], 'Por estado', required=True),
        'salida': fields.boolean('Salida'),
        'entrada': fields.boolean('Entrada'),
        'intermedio': fields.boolean('Intermedio'),
        'flujo': fields.boolean('Maneja Flujo'),
        'state': fields.selection([('buscar','Buscar'),('actualizar','Actualizar'),('hecho','Hecho')]),
        'data': fields.binary('Archivo', readonly=True),
        'ppu_ids' : fields.many2many('posicion.por.ubicacion', 'rev_ppu_rel','rev_id', 'ppu_id','Posiciones'),
        'company_id': fields.many2one('res.company', 'Compania', select=1),
    }

    _defaults = {
        'state': 'buscar',
        'flujo': False,
        'company_id': lambda self, cr, uid, c: self._get_company_id(cr, uid, context=c),
    }

    def buscar_posiciones(self, cr, uid, ids, context=None):
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        for rev in self.browse(cr, uid, ids):
            criterio_busqueda = []
            criterio_busqueda.append(('location_id','=',rev.location_id.id))
            if rev.salida:
                criterio_busqueda.append(('salida','=',True))
            if rev.entrada:
                criterio_busqueda.append(('entrada','=',True))
            if rev.intermedio:
                criterio_busqueda.append(('intermedio','=',True))
            if rev.estado != 'todas':
                criterio_busqueda.append(('state','=',rev.estado))
            if rev.tipo_almacenamiento != 'todas':
                criterio_busqueda.append(('tipo_almacenamiento','=',rev.tipo_almacenamiento))
            posiciones_ids = posicion_obj.search(cr, uid, criterio_busqueda)
            self.write(cr, uid, [rev.id], {'ppu_ids':[(6, rev.id, posiciones_ids)],'state':'actualizar','encontradas':int(len(posiciones_ids))})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'revisa.posicion.por.ubicacion.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': rev.id,
                'views': [(False, 'form')],
                'target': 'new',
                }
        return True

    def chequea_vacio(self, cr, uid, posicion):
        res = '-'
        if not posicion.vacio:
            res = 'Falso'
        else:
            res = 'Verdadero'
        return res

    def chequea_actualiza_flujo(self, cr, uid, rev, posicion_obj, posicion):
        res = '-'
        if rev.flujo:
            res = 'Verdadero'
            posicion_obj.write(cr, uid, [posicion.id], {'flujo':True})
        else:
            res = 'Falso'
            posicion_obj.write(cr, uid, [posicion.id], {'flujo':False})
        return res

    def actualiza_posiciones(self, cr, uid, ids, context=None):
        posicion_obj = self.pool.get('posicion.por.ubicacion')
        mensaje = '"Posicion","Disponible","Flujo"\n'
        for rev in self.browse(cr, uid, ids):
            lista_posiciones = []
            for posicion in rev.ppu_ids:
                lista_posiciones.append(posicion.id)
                mensaje += '"' + posicion.name + '",'
                mensaje += '"' + self.chequea_vacio(cr, uid, posicion) + '",'
                mensaje += '"' + self.chequea_actualiza_flujo(cr, uid, rev, posicion_obj, posicion) + '"\n'

            buf = cStringIO.StringIO()
            buf.write(mensaje)
            out = base64.encodestring(buf.getvalue())
            buf.close()

            nombre = rev.location_id.name + '.csv'

            self.write(cr, uid, [rev.id], {'state':'hecho','data':out,'name':nombre})
            
            ahora = datetime.now()
            self.pool.get('posicion.por.ubicacion').write(cr, uid, lista_posiciones, {'last_check_date':ahora,'last_check_uid':uid})

            mensaje = ''
            out = ''
            lista_posiciones = []
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'revisa.posicion.por.ubicacion.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': rev.id,
                'views': [(False, 'form')],
                'target': 'new',
                }
        return True

revisa_posicion_por_ubicacion_wizard()

#------------------------------------------
# Crear Flujo Wizard
#------------------------------------------

class crear_flujo_wizard(osv.osv_memory):
    _name = "crear.flujo.wizard"

    def _get_company_id(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = user.company_id and user.company_id.id or False
        return res

    def _product_default_get(self, cr, uid, active_id, context=None):
        res = False
        if active_id:
            ppul_obj = self.pool.get('posicion.por.ubicacion.linea')
            ppul = ppul_obj.browse(cr, uid, active_id)
            res = ppul.product_id.id
        return res

    def _location_default_get(self, cr, uid, active_id, context=None):
        res = False
        if active_id:
            ppul_obj = self.pool.get('posicion.por.ubicacion.linea')
            ppul = ppul_obj.browse(cr, uid, active_id)
            res = ppul.location_id.id
        return res

    def _stock_origen_default_get(self, cr, uid, active_id, context=None):
        res = 0.0
        if active_id:
            ppul_obj = self.pool.get('posicion.por.ubicacion.linea')
            ppul = ppul_obj.browse(cr, uid, active_id)
            for linea in ppul.ppu_id.ppu_desde_id.posiciones_lineas_ids:
                if linea.product_id.id == ppul.product_id.id:
                    res = linea.cantidad
        return res

    _columns = {
        'name': fields.char('Nombre', size=32),
        'product_id' : fields.many2one('product.product', 'Producto', readonly=True),
        'product_qty': fields.float('Cantidad a mover'),
        'stock_origen': fields.float('Cantidad en origen', readonly=True),
        'company_id': fields.many2one('res.company', 'Compania', readonly=True),
        'location_id' : fields.many2one('stock.location', 'Ubicacion', readonly=True),
        'ppul_id': fields.many2one('posicion.por.ubicacion.linea', 'Linea', readonly=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self._get_company_id(cr, uid, context=c),
        'product_id': lambda self, cr, uid, c: self._product_default_get(cr, uid, c.get('active_id', False), context=c),
        'location_id': lambda self, cr, uid, c: self._location_default_get(cr, uid, c.get('active_id', False), context=c),
        'stock_origen': lambda self, cr, uid, c: self._stock_origen_default_get(cr, uid, c.get('active_id', False), context=c),
        'ppul_id': lambda x, y, z, c: c.get('active_id', False),
    }

    def chequea_compania(self, cr, uid, cfw):

        res = False
        comp_usuario = False
        comp_cfw = False

        comp_user = self.pool.get('res.users').browse(cr, uid, uid).company_id

        if comp_user:
            comp_usuario = comp_user.id
        if cfw.company_id:
            comp_cfw = cfw.company_id.id

        if comp_usuario == comp_cfw:
            if comp_usuario:
                res = comp_usuario

        return res

    def crear_flujo_entre_lineas(self, cr, uid, cfw):
        #Primero buscar flujos pendientes para este destino, si los hay
        #no permitir generar un nuevo flujo y solictar que se procese el
        #pendiente primero
        flujo_obj = self.pool.get('flujo.entre.posiciones')
        criterio_pendientes = []
        criterio_pendientes.append(('state','not in',('hecho','cancelado')))
        criterio_pendientes.append(('product_id','=',cfw.product_id.id))
        criterio_pendientes.append(('linea_destino_id','=',cfw.ppul_id.id))
        flujos_pendientes_ids = flujo_obj.search(cr, uid, criterio_pendientes)
        if flujos_pendientes_ids:
            raise osv.except_osv('Error','Hay flujos pendientes para esta posicion.\nAntes de crear uno nuevo, procese los pendientes.')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'flujo.entre.posiciones',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': "[('id','in',"+str(flujos_pendientes_ids)+")]",
                'view_id': ['stock_flujo_entre_posiciones_tree'],
                'target': 'current',
                }
        else:
            flujo_ids = []
            posicion_origen = cfw.ppul_id.ppu_id.ppu_desde_id or False
            linea_origen = False
            if posicion_origen:
                for line in posicion_origen.posiciones_lineas_ids:
                    if cfw.product_id.id == line.product_id.id:
                        linea_origen = line
            posicion_destino = cfw.ppul_id.ppu_id
            linea_destino = cfw.ppul_id
            cantidad_a_mover = cfw.product_qty
            if not posicion_origen or not linea_origen:
                return True
            vals_creacion_flujo = dict()
            vals_creacion_flujo['name'] = str(posicion_origen.name) + ' ' + str(posicion_destino.name) + ' ' + str(linea_destino.product_id.name)
            vals_creacion_flujo['product_id'] = linea_destino.product_id.id
            vals_creacion_flujo['ppu_desde_id'] = posicion_origen.id
            vals_creacion_flujo['ppu_hasta_id'] = posicion_destino.id
            vals_creacion_flujo['linea_origen_id'] = linea_origen.id
            vals_creacion_flujo['linea_destino_id'] = linea_destino.id
            vals_creacion_flujo['cantidad'] = cantidad_a_mover
            vals_creacion_flujo['location_id'] = cfw.location_id.id
            vals_creacion_flujo['state'] = 'pendiente'
            vals_creacion_flujo['company_id'] = cfw.company_id.id
            flujo_id = flujo_obj.create(cr, uid, vals_creacion_flujo)
            flujo_ids.append(flujo_id)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'flujo.entre.posiciones',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': "[('id','in',"+str(flujo_ids)+")]",
                'target': 'current',
                }
        return True

    def crear_flujo(self, cr, uid, ids, context=None):
        posicion_linea_obj = self.pool.get('posicion.por.ubicacion.linea')
        res = True
        for cfw in self.browse(cr, uid, ids):
            if cfw.product_qty < 1:
                raise osv.except_osv('Error','No puede crear un flujo por una cantidad menor a uno.')
                return False
            if cfw.product_qty > cfw.stock_origen:
                raise osv.except_osv('Error','No puede mover mas cantidad (%s) de la que hay en el origen (%s).'%(cfw.product_qty,cfw.stock_origen))
                return False
            if cfw.ppul_id.capacidad:
                if (cfw.ppul_id.cantidad + cfw.product_qty) > cfw.ppul_id.capacidad:
                    raise osv.except_osv('Error','No puede ingresar una cantidad mayor a la capacidad maxima (%s).'%(cfw.ppul_id.capacidad,))
                    return False
            company_id = self.chequea_compania(cr, uid, cfw)
            if company_id:
                    res = self.crear_flujo_entre_lineas(cr, uid, cfw)
        return res
