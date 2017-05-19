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

import logging

class traza_envios_wizard(osv.osv_memory):
    _name = "traza.envios.wizard"

    tew_estados_ot = [
        ('esperando','Esperando'),
        ('despachado','Despachado'),
        ('entransito','En transito'),
        ('enreparto','En reparto'),
        ('entregado','Entregado'),
        ('devuelto','Devuelto'),
        ('perdido','Perdido'),
        ('cancelado','Cancelado'),
    ]

    tew_tipo_ot = [
        ('padre','Padre'),
        ('hija','Hija'),
    ]

    _columns = {
        'name': fields.char('Numero', size=48, select=True),
        'picking_id': fields.many2one('stock.picking','Albaran'),
        'caja_id': fields.many2one('stock.caja.transporte','Caja'),
        'tew_id': fields.many2one('traza.envios.wizard','TEW'),
        'ot_id': fields.many2one('stock.orden.transporte','OT Padre'),
        'line_ids': fields.one2many('traza.envios.wizard', 'tew_id', 'OT Hijas'),
        'state': fields.selection(tew_estados_ot, 'Estado'),
        'ot_type': fields.selection(tew_tipo_ot, 'Tipo', readonly=True),
        'generar_numero': fields.boolean('Generar OT'),
        'generar_numero_ot_linea': fields.boolean('Generar OT para cada linea'),
        'paso': fields.selection([('uno','Uno'),('dos','Dos'),('tres','Tres')], 'Paso', readonly=True),
    }

    _defaults = {
        'state': 'esperando',
        'ot_type': 'padre',
        'paso': 'uno',
        'generar_numero': True,
        'generar_numero_ot_linea': False,
    }

    def siguiente_paso(self, cr, uid, ids, context=None):
        vals = dict()
        ot_obj = self.pool.get('stock.orden.transporte')
        for tew in self.browse(cr, uid, ids):
            ot_ids = False
            if tew.name:
                ot_ids = ot_obj.search(cr, uid, [('name','=',tew.name)])
            if ot_ids :
                raise osv.except_osv('Error!', 'No se puede continuar.\nYa existe una OT con este numero.')
                return False
            vals['paso'] = 'dos'
            if not tew.name:
                if not tew.generar_numero:
                    raise osv.except_osv('Error!', 'No se puede continuar, falta OT o seleccionar Generar OT.')
                    return False
                else:
                    secuencia = self.pool.get('ir.sequence').get(cr, uid, 'traza.orden.transporte')
                    vals['name'] = secuencia
            self.write(cr, uid, [tew.id], vals)
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'traza.envios.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': tew.id,
                    'views': [(False, 'form')],
                    'target': 'new',
                    }

    def get_company_id(self, cr, uid, ids, line, context):
        compania_destino_comun = False
        pick_id = line.picking_id.id
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

    def boton_crear_ot(self, cr, uid, ids, context=None):
        vals = dict()
        for tew in self.browse(cr, uid, ids):
            ot_padre_id = False
            vals['paso'] = 'tres'
            self.write(cr, uid, [tew.id], vals)
            ot_obj = self.pool.get('stock.orden.transporte')
            ot_padre_ids = ot_obj.search(cr, uid, [('name','=',tew.name),('ot_type','=','padre')])
            ot_hijas_ids = ot_obj.search(cr, uid, [('name','=',tew.name),('ot_type','=','hija')])
            if ot_hijas_ids :
                raise osv.except_osv('Error!', 'No se puede continuar.\nYa existe una OT hija con este numero.')
                return False
            if ot_padre_ids and len(ot_padre_ids) == 1:
                ot_padre_id = ot_padre_ids[0]
            if ot_padre_ids and len(ot_padre_ids) > 1:
                raise osv.except_osv('Error!', 'No se puede continuar, se encontaron demasiadas OT padre con esta referencia.')
                return False
            if not ot_padre_ids:
                user_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
                ot_padre_id = ot_obj.create(cr, uid, {'name': tew.name, 'company_id': user_company_id})
            if not ot_padre_id:
                raise osv.except_osv('Error!', 'No se puede continuar, no existe una OT padre.')
                return False
            if tew.state in ('entregado','cancelado','devuelto','perdido'):
                raise osv.except_osv('Error!', 'No se puede continuar, esta creando o asignando una OT.\nDebe seleccionar un estado distinto a\nEntregado, Devuelto, Perdido o Cancelado\nEsa informacion la debe actualizar desde el asistente creado para ello.')
                return False
            for line in tew.line_ids:
                if line.picking_id.orden_transporte_id:
                    raise osv.except_osv('Error!', 'No se puede continuar, este Albaran (%s) ya tiene OT asignada (%s).'%(line.picking_id.name,line.picking_id.orden_transporte_id.name))
                    return False
                ot_hija_name = tew.name
                if tew.generar_numero_ot_linea:
                    ot_hija_name = self.pool.get('ir.sequence').get(cr, uid, 'traza.orden.transporte')
                compania_id = self.get_company_id(cr, uid, ids, line, context)
                ot_hija_name = ot_hija_name + "OTH"
                vals_hija = {
                    'name': ot_hija_name,
                    'ot_type': 'hija',
                    'ot_id': ot_padre_id,
                    'picking_id': line.picking_id and line.picking_id.id or False,
                    'state': tew.state,
                    'company_id': compania_id,
                }
                logger = logging.getLogger('log.boton_crear_ot')
                logger.warn(line.caja_id)
                if line.caja_id:
                    vals_hija['cajas_ids'] = [(4, line.caja_id.id)]
                ot_obj.create(cr, uid, vals_hija)
                self.write(cr, uid, [line.id], {'name': ot_hija_name})
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'traza.envios.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': tew.id,
                    'views': [(False, 'form')],
                    'target': 'new',
                    }

    def boton_cerrar(self, cr, uid, ids, context=None):
        ot_obj = self.pool.get('stock.orden.transporte')
        picking_obj = self.pool.get('stock.picking')
        for tew in self.browse(cr, uid, ids):
            ot_padre_ids = ot_obj.search(cr, uid, [('name','=',tew.name),('ot_type','=','padre')])
            if ot_padre_ids and len(ot_padre_ids) == 1:
                ot_padre = ot_obj.browse(cr, uid, ot_padre_ids[0])
                lista_ot = []
                for line in ot_padre.ot_ids:
                    lista_ot.append(line.id)
                    if line.picking_id.orden_transporte_id:
                        raise osv.except_osv('Error!', 'No se puede continuar, este Albaran (%s) ya tiene OT asignada (%s).'%(line.picking_id.name,line.picking_id.orden_transporte_id.name))
                        return False
                    else:
                        picking_obj.write(cr, uid, [line.picking_id.id], {'orden_transporte_id': line.id})
                lista_ot.append(ot_padre.id)
                ot_obj.write(cr, uid, lista_ot, {'state': tew.state})
            else:
                raise osv.except_osv('Error!', 'No se puede continuar, se encontaron demasiadas OT padre con esta referencia.')
                return False
        return {'type': 'ir.actions.act_window_close'}

    def buscar_ot(self, cr, uid, ids, context=None):
        ot_obj = self.pool.get('stock.orden.transporte')
        vals = dict()
        for tew in self.browse(cr, uid, ids):
            vals['paso'] = 'dos'
            #self.write(cr, uid, [tew.id], vals)
            ot_ids = ot_obj.search(cr, uid, [('name','=',tew.name)])
            if not ot_ids:
                raise osv.except_osv('Error!', 'No se puede continuar, no se encuentra una OT con esa referencia.')
                return False
            if ot_ids and len(ot_ids) > 1:
                raise osv.except_osv('Error!', 'No se puede continuar, hay mas de una OT con esa referencia.')
                return False
            if len(ot_ids) == 1:
                ot = ot_obj.browse(cr, uid, ot_ids[0])
                vals['state'] = ot.state or False
                vals['ot_type'] = ot.ot_type or False
                if ot.ot_type == 'hija':
                    vals['picking_id'] = ot.picking_id and ot.picking_id.id or False
                    vals['ot_id'] = ot.ot_id and ot.ot_id.id or False
                for oth in ot.ot_ids:
                    self.create(cr, uid, {'name':oth.name,'picking_id':oth.picking_id.id, 'tew_id':tew.id, 'ot_id': oth.id})
            self.write(cr, uid, [tew.id], vals)
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'traza.envios.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': tew.id,
                    'views': [(False, 'form')],
                    'context': {'form_view_ref' : 'traza_envios.traza_envios_upd_wizard_form_view'},
                    'target': 'new',
                    }

    def actualizar_ot_hija(self, cr, uid, oth_obj, tew, context=None):
        ot_obj = self.pool.get('stock.orden.transporte')
        picking_obj = self.pool.get('stock.picking')
        oth_vals = dict()
        if oth_obj.state != tew.state:
            oth_vals['state'] = tew.state
        if oth_obj.picking_id.id != tew.picking_id.id:
            if not tew.picking_id.orden_transporte_id:
                oth_vals['picking_id'] = tew.picking_id.id
            else:
                raise osv.except_osv('Error!', 'El albaran %s ya tiene asigada una OT %s.'%(tew.picking_id.name,tew.picking_id.orden_transporte_id.name))
                return False
        oth_state = oth_vals.get('state', False)
        if oth_state and oth_state == 'entregado':
            #Disparar entrega en el albaran
            if not tew.picking_id.entregado:
                picking_obj.entregado_met(cr, uid, [tew.picking_id.id], context=context)
                logger = logging.getLogger('log.se_dispara_la_entrega')
                logger.warn('Disparar entrega en el albaran')
        if oth_vals:
            ot_obj.write(cr, uid, [oth_obj.id], oth_vals)
            return True
        else:
            return False

    def actualizar_ot(self, cr, uid, ids, context=None):
        ot_obj = self.pool.get('stock.orden.transporte')
        vals = dict()
        for ntew in self.browse(cr, uid, ids):
            #Actualizo las lineas antes de utilizarlas
            #para escribir los ot hijas.
            for ltew in ntew.line_ids:
                self.write(cr, uid, [ltew.id], {'state':ntew.state})
        for tew in self.browse(cr, uid, ids):
            vals['paso'] = 'tres'
            self.write(cr, uid, [tew.id], vals)
            ot_ids = ot_obj.search(cr, uid, [('name','=',tew.name)])
            for ot in ot_obj.browse(cr, uid, ot_ids):
                if ot.ot_type == 'padre':
                    if ot.state != tew.state:
                        ot_obj.write(cr, uid, [ot.id], {'state':tew.state})
                    for oth in ot.ot_ids:
                        for line in tew.line_ids:
                            if line.ot_id:
                                if oth.id == line.ot_id.id:
                                    self.actualizar_ot_hija(cr, uid, oth, line, context=context)
                            else:
                                #Quizas no existe esta OT y se deba crear ahora.
                                ot_ids = ot_obj.search(cr, uid, [('name','=',line.name)])
                                if not ot_ids:
                                    if line.picking_id.orden_transporte_id:
                                        raise osv.except_osv('Error!', 'No se puede continuar, este Albaran (%s) ya tiene OT asignada (%s).'%(line.picking_id.name,line.picking_id.orden_transporte_id.name))
                                        return False
                                    else:

                                        ot_hija_name = 'SIN NOMBRE'
                                        secuencia_ot = self.pool.get('ir.sequence').get(cr, uid, 'traza.orden.transporte')
                                        if tew.generar_numero_ot_linea:
                                            ot_hija_name = secuencia_ot
                                        else:
                                            ot_hija_name = tew.name or secuencia_ot
                                        ot_hija_name = ot_hija_name + 'OTH'

                                        compania_id = self.get_company_id(cr, uid, ids, line, context)
                                        oth_create_vals = dict()
                                        oth_create_vals['name'] = ot_hija_name
                                        oth_create_vals['picking_id'] = line.picking_id.id
                                        oth_create_vals['ot_id'] = ot.id
                                        oth_create_vals['state'] = tew.state
                                        oth_create_vals['ot_type'] = 'hija'
                                        oth_create_vals['company_id'] = compania_id
                                        new_oth_id = ot_obj.create(cr, uid, oth_create_vals)
                                        self.write(cr, uid, [line.id], {'ot_id': new_oth_id, 'name': ot_hija_name})
                elif ot.ot_type == 'hija':
                    self.actualizar_ot_hija(cr, uid, ot, tew, context=context)
                else:
                    raise osv.except_osv('Error!', 'No se puede continuar.\nNo hay tipo de OT.')
                    return False
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'traza.envios.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': tew.id,
                'views': [(False, 'form')],
                'context': {'form_view_ref' : 'traza_envios.traza_envios_upd_wizard_form_view'},
                'target': 'new',
                }

    def boton_cerrar_ot(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

traza_envios_wizard()

class agrupar_ot(osv.osv_memory):
    _name = 'agrupar.ot'

    _columns = {
        'company_id': fields.many2one('res.company', 'Compania', required=True),
        'resultado': fields.text('Resultado', readonly=True),
        'state': fields.selection([('draft','Borrador'),('done','Hecho')], 'Estado'),
    }

    _defaults = {
        'state': 'draft',
    }

    def agrupar(self, cr, uid, ids, context=None):
        ot_obj = self.pool.get('stock.orden.transporte')
        resultado = 'SIN RESULTADOS'
        for ag_ot in self.browse(cr, uid, ids):
            crit_busq = []
            crit_busq.append(('ot_type','=','hija'))
            crit_busq.append(('company_id','=',ag_ot.company_id.id))
            crit_busq.append(('state','=','esperando'))
            crit_busq.append(('ot_id','=',False))
            ot_ids = ot_obj.search(cr, uid, crit_busq)
            if ot_ids:
                resultado = ''
                secuencia = self.pool.get('ir.sequence').get(cr, uid, 'traza.orden.transporte')
                user_company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
                ot_padre_id = ot_obj.create(cr, uid, {'name': secuencia, 'company_id': user_company_id})
                ot_obj.write(cr, uid, ot_ids, {'ot_id': int(ot_padre_id)})
                for ot in ot_obj.browse(cr, uid, ot_ids):
                    resultado += 'La OT '+str(ot.name)+' fue actualizada con la OT Padre '+str(ot.ot_id.name)+'\n'
                self.write(cr, uid, [ag_ot.id], {'resultado': resultado, 'state':'done'})
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'agrupar.ot',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': ag_ot.id,
                    'views': [(False, 'form')],
                    'context': {},
                    'target': 'new',
                    }
        return True
