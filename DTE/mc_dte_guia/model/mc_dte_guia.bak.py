#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   DTE Guia Chile OpenERP 7
#   Copyright (C) 2016 Cesar Lopez Aguillon Mall Connection
#   <http://www.mallconnection.org>.
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
#from openerp import netsvc
from openerp import tools
#from os import sys
from libredte.sdk import LibreDTE
from bs4 import BeautifulSoup

import collections
import base64
import unicodedata
import logging

#elimina_tildes de Victor Alvarez https://gist.github.com/victorono/7633010
def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()

class mc_dte(osv.osv):
    _inherit = 'mc.dte'

    _columns = {
        'picking_out_id': fields.many2one('stock.picking.out', 'Guia', readonly=True),
    }

mc_dte()

class stock_journal(osv.osv):
    _inherit = 'stock.journal'

    _columns = {
        'sii_dte': fields.char('Codigo DTE SII', size=8),
        'mc_dte_config_id': fields.many2one('mc.dte.config', 'Configuracion DTE'),
        'reporte_dte_id': fields.many2one('ir.actions.report.xml', 'Reporte DTE'),
    }

stock_journal()

#class stock_picking_out(osv.osv):
#    _inherit = 'stock.picking.out'

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'mc_dte_id': fields.many2one('mc.dte', 'Registro DTE', readonly=True),
        'numero_guia': fields.char('N° guia', size=64, readonly=True),
        'patente_transporte': fields.char('Patente', size=18),
        'chofer_id': fields.many2one('res.partner', 'Chofer'),
    }

    def imprime_dte(self, cr, uid, picking, context=None):
        #self.write(cr, uid, [picking.id], {'sent': True}, context=context)
        datas = {
             'ids': [picking.id],
             'model': 'stock.picking.out',
             'form': self.read(cr, uid, picking.id, context=context)
        }
        if picking.stock_journal_id:
            if picking.stock_journal_id.reporte_dte_id:
                report_name = picking.stock_journal_id.reporte_dte_id.report_name
            else:
                report_name = 'guia.electronica.webkit'
        else:
            report_name = 'guia.electronica.webkit'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            'nodestroy' : True
        }

    def imprimir_guia(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe imprimir un documento a la vez.'
        picking = self.browse(cr, uid, ids[0], context=context)
        if picking.mc_dte_id:
            if picking.mc_dte_id.imprimir:
                return self.imprime_dte(cr, uid, picking, context=context)
            else:
                raise osv.except_osv("Error","Primero debe actualizar el estado del DTE y este no debe ser Rechazado.")
                return False
        else:
            return True

    def consultar_estado_dte(self, cr, uid, ids, context=None):
        dte_obj = self.pool.get('mc.dte')
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.mc_dte_id:
                mc_dte_config_id = picking.stock_journal_id.mc_dte_config_id
                detalle = dte_obj.consultar_estado(cr, uid, [picking.mc_dte_id.id], mc_dte_config_id, context=context)
                mensaje = detalle
                self.message_post(cr, uid, [picking.id], body=tools.ustr(mensaje), context=context)
        return True

    def actualizar_estado_dte(self, cr, uid, ids, context=None):
        dte_obj = self.pool.get('mc.dte')
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.mc_dte_id:
                mc_dte_config_id = picking.stock_journal_id.mc_dte_config_id
                estado, track_id = dte_obj.actualizar_estado(cr, uid, [picking.mc_dte_id.id], mc_dte_config_id, context=context)
                mensaje = '<b>DTE actualizado:</b><br>'
                mensaje += 'Revision: ' + str(estado) + '<br>'
                mensaje += 'Track ID: ' + str(track_id) + '<br>'
                self.message_post(cr, uid, [picking.id], body=tools.ustr(mensaje), context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        logger = logging.getLogger('action_done stock picking')
        res = super(stock_picking, self).action_done(cr, uid, ids, context=context)
        self.generar_guia(cr, uid, ids, context=context)
        logger.warn(res)
        return res

    def generar_dicc_usuario(self, cr, uid, picking, context=None):
        res = collections.OrderedDict()
        res['servidor'] = picking.stock_journal_id.mc_dte_config_id.servidor_dte
        res['sucursal_sii'] = picking.stock_journal_id.mc_dte_config_id.sucursal_sii
        res['ruta_archivos'] = picking.stock_journal_id.mc_dte_config_id.ruta_archivos
        res['dte_permitidos'] = [dpe.codigo_sii for dpe in picking.stock_journal_id.mc_dte_config_id.dte_permitidos]
        res['hash_dte'] = picking.stock_journal_id.mc_dte_config_id.hash_tienda
        res['dte_pruebas'] = picking.stock_journal_id.mc_dte_config_id.dte_pruebas
        res['enviar_num_folio'] = picking.stock_journal_id.mc_dte_config_id.enviar_num_folio
        res['tipo_dte'] = 'picking_out_id'
        res['id_externo'] = picking.id
        return res

    def generar_dicc_dte(self, cr, uid, picking, context=None):
        if not picking.sale_id:
            return True
        res = collections.OrderedDict()
        res['Encabezado'] = collections.OrderedDict()
        res['Encabezado']['IdDoc'] = collections.OrderedDict()
        res['Encabezado']['Emisor'] = collections.OrderedDict()
        res['Encabezado']['Receptor'] = collections.OrderedDict()
        res['Encabezado']['IdDoc']['TipoDTE'] = picking.stock_journal_id.sii_dte
        res['Encabezado']['IdDoc']['Folio'] = picking.numero_guia
        res['Encabezado']['IdDoc']['IndTraslado'] = picking.sale_id.tipo_movimiento
        res['Encabezado']['Emisor']['RUTEmisor'] = picking.stock_journal_id.mc_dte_config_id.rutemisor
        res['Encabezado']['Emisor']['RznSoc'] = picking.stock_journal_id.mc_dte_config_id.razonsocial
        res['Encabezado']['Emisor']['GiroEmis'] = picking.stock_journal_id.mc_dte_config_id.giroemisor
        res['Encabezado']['Emisor']['Acteco'] = picking.stock_journal_id.mc_dte_config_id.acteco
        res['Encabezado']['Emisor']['DirOrigen'] = picking.stock_journal_id.mc_dte_config_id.direccionorigen
        res['Encabezado']['Emisor']['CmnaOrigen'] = picking.stock_journal_id.mc_dte_config_id.comunaorigen
        res['Encabezado']['Emisor']['CiudadOrigen'] = picking.stock_journal_id.mc_dte_config_id.ciudadorigen
        res['Encabezado']['Receptor']['RUTRecep'] = picking.sale_id.partner_id.rut_cliente
        res['Encabezado']['Receptor']['RznSocRecep'] = picking.sale_id.partner_id.name
        res['Encabezado']['Receptor']['GiroRecep'] = picking.sale_id.partner_id.giro_cliente
        res['Encabezado']['Receptor']['DirRecep'] = picking.sale_id.partner_id.street 
        res['Encabezado']['Receptor']['CmnaRecep'] = picking.sale_id.partner_id.state_id.name
        
        if picking.carrier_id or picking.sale_id.partner_id != picking.partner_id:
            res['Encabezado']['Transporte'] = collections.OrderedDict()
        
        # Transporte
        if picking.carrier_id:
            res['Encabezado']['Transporte']['RUTTrans'] = picking.carrier_id.partner_id.rut_cliente
            if picking.patente_transporte:
                res['Encabezado']['Transporte']['Patente'] = picking.patente_transporte
            if picking.chofer_id:
                res['Encabezado']['Transporte']['Chofer'] = collections.OrderedDict()
                res['Encabezado']['Transporte']['Chofer']['RUTChofer'] = picking.chofer_id.rut_cliente
                res['Encabezado']['Transporte']['Chofer']['NombreChofer'] = picking.chofer_id.name
        
        if picking.sale_id.partner_id != picking.partner_id:
            res['Encabezado']['Transporte']['DirDest'] = picking.partner_id.street
            res['Encabezado']['Transporte']['CmnaDest'] = picking.partner_id.state_id.name
        
        res['Detalle'] = list()

        # obtener las lineas desde el pedido de venta
        lineas_venta = picking.sale_id.order_line
        for linea in lineas_venta:
            linea_dicc = collections.OrderedDict()
            if linea.product_id.default_code:
                linea_dicc['CdgItem'] = collections.OrderedDict()
                linea_dicc['CdgItem']['TpoCodigo'] = 'INT1'
                linea_dicc['CdgItem']['VlrCodigo'] = linea.product_id.default_code
            linea_dicc['NmbItem'] = linea.product_id.name_template
            linea_dicc['QtyItem'] = linea.quantity
            linea_dicc['PrcItem'] = linea.price_unit

            if linea.discount:
                linea_dicc['DescuentoPct'] = linea.discount

            res['Detalle'] += [linea_dicc]

        if not res['Detalle']:
            raise osv.except_osv("Error","El documento no contiene lineas.")
            return False

        return res

    def generar_guia(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe generar un documento a la vez.'
        dte_obj = self.pool.get('mc.dte')
        picking = self.browse(cr, uid, ids[0])
        if picking.sale_id:
            diario = picking.stock_journal_id
            if diario and diario.mc_dte_config_id and diario.sii_dte:
                dicc_u = self.generar_dicc_usuario(cr, uid, picking, context)
                dicc_d = self.generar_dicc_dte(cr, uid, picking, context)
                mc_dte_id = dte_obj.dte_sii(cr, uid, dicc_d, dicc_u, context)
                if mc_dte_id != 0:
                    self.write(cr, uid, [picking.id], {'mc_dte_id':mc_dte_id})
                    mc_dte = dte_obj.browse(cr, uid, mc_dte_id)
                    mensaje = '<b>DTE creado:</b><br>'
                    mensaje += 'Tipo: ' + str(mc_dte.codigo_sii) + '<br>'
                    mensaje += 'Folio: ' + str(mc_dte.folio_dte_sii) + '<br>'
                    mensaje += 'Track ID: ' + str(mc_dte.track_id) + '<br>'
                    self.message_post(cr, uid, [picking.id], body=tools.ustr(mensaje), context=context)
                    dte_obj.write(cr, uid, [mc_dte_id], {'picking_out_id': picking.id})
        return True
stock_picking()
#stock_picking_out()


class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'

#class stock_picking(osv.osv):
#    _inherit = 'stock.picking'

    _columns = {
        'mc_dte_id': fields.many2one('mc.dte', 'Registro DTE', readonly=True),
        'numero_guia': fields.char('N° guia', size=64, readonly=True),
        'patente_transporte': fields.char('Patente', size=18),
        'chofer_id': fields.many2one('res.partner', 'Chofer'),
    }

    def imprime_dte(self, cr, uid, picking, context=None):
        logger = logging.getLogger('imprime dte out')
        logger.warn('## out ##')
        #self.write(cr, uid, [picking.id], {'sent': True}, context=context)
        datas = {
             'ids': [picking.id],
             'model': 'stock.picking.out',
             'form': self.read(cr, uid, picking.id, context=context)
        }
        if picking.stock_journal_id:
            if picking.stock_journal_id.reporte_dte_id:
                report_name = picking.stock_journal_id.reporte_dte_id.report_name
            else:
                report_name = 'guia.electronica.webkit'
        else:
            report_name = 'guia.electronica.webkit'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            'nodestroy' : True
        }

    def imprimir_guia(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe imprimir un documento a la vez.'
        picking = self.browse(cr, uid, ids[0], context=context)
        if picking.mc_dte_id:
            if picking.mc_dte_id.imprimir:
                return self.imprime_dte(cr, uid, picking, context=context)
            else:
                raise osv.except_osv("Error","Primero debe actualizar el estado del DTE y este no debe ser Rechazado.")
                return False
        else:
            return True

    def consultar_estado_dte(self, cr, uid, ids, context=None):
        logger = logging.getLogger('consultar estado out')
        logger.warn('## out ##')
        dte_obj = self.pool.get('mc.dte')
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.mc_dte_id:
                mc_dte_config_id = picking.stock_journal_id.mc_dte_config_id
                detalle = dte_obj.consultar_estado(cr, uid, [picking.mc_dte_id.id], mc_dte_config_id, context=context)
                mensaje = detalle
                self.message_post(cr, uid, [picking.id], body=tools.ustr(mensaje), context=context)
        return True

    def actualizar_estado_dte(self, cr, uid, ids, context=None):
        logger = logging.getLogger('actualizar estado out')
        logger.warn('## out ##')
        dte_obj = self.pool.get('mc.dte')
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.mc_dte_id:
                mc_dte_config_id = picking.stock_journal_id.mc_dte_config_id
                estado, track_id = dte_obj.actualizar_estado(cr, uid, [picking.mc_dte_id.id], mc_dte_config_id, context=context)
                mensaje = '<b>DTE actualizado:</b><br>'
                mensaje += 'Revision: ' + str(estado) + '<br>'
                mensaje += 'Track ID: ' + str(track_id) + '<br>'
                self.message_post(cr, uid, [picking.id], body=tools.ustr(mensaje), context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        logger = logging.getLogger('action_done')
        res = super(stock_picking_out, self).action_done(cr, uid, ids, context=context)
        logger.warn(res)
        return res

    def generar_dicc_usuario(self, cr, uid, picking, context=None):
        res = collections.OrderedDict()
        res['servidor'] = picking.stock_journal_id.mc_dte_config_id.servidor_dte
        res['sucursal_sii'] = picking.stock_journal_id.mc_dte_config_id.sucursal_sii
        res['ruta_archivos'] = picking.stock_journal_id.mc_dte_config_id.ruta_archivos
        res['dte_permitidos'] = [dpe.codigo_sii for dpe in picking.stock_journal_id.mc_dte_config_id.dte_permitidos]
        res['hash_dte'] = picking.stock_journal_id.mc_dte_config_id.hash_tienda
        res['dte_pruebas'] = picking.stock_journal_id.mc_dte_config_id.dte_pruebas
        res['enviar_num_folio'] = picking.stock_journal_id.mc_dte_config_id.enviar_num_folio
        res['tipo_dte'] = 'picking_out_id'
        res['id_externo'] = picking.id
        return res

    def generar_dicc_dte(self, cr, uid, picking, context=None):
        if not picking.sale_id:
            return True
        res = collections.OrderedDict()
        res['Encabezado'] = collections.OrderedDict()
        res['Encabezado']['IdDoc'] = collections.OrderedDict()
        res['Encabezado']['Emisor'] = collections.OrderedDict()
        res['Encabezado']['Receptor'] = collections.OrderedDict()
        res['Encabezado']['IdDoc']['TipoDTE'] = picking.stock_journal_id.sii_dte
        res['Encabezado']['IdDoc']['Folio'] = picking.numero_guia
        res['Encabezado']['IdDoc']['IndTraslado'] = picking.sale_id.tipo_movimiento
        res['Encabezado']['Emisor']['RUTEmisor'] = picking.stock_journal_id.mc_dte_config_id.rutemisor
        res['Encabezado']['Emisor']['RznSoc'] = picking.stock_journal_id.mc_dte_config_id.razonsocial
        res['Encabezado']['Emisor']['GiroEmis'] = picking.stock_journal_id.mc_dte_config_id.giroemisor
        res['Encabezado']['Emisor']['Acteco'] = picking.stock_journal_id.mc_dte_config_id.acteco
        res['Encabezado']['Emisor']['DirOrigen'] = picking.stock_journal_id.mc_dte_config_id.direccionorigen
        res['Encabezado']['Emisor']['CmnaOrigen'] = picking.stock_journal_id.mc_dte_config_id.comunaorigen
        res['Encabezado']['Emisor']['CiudadOrigen'] = picking.stock_journal_id.mc_dte_config_id.ciudadorigen
        res['Encabezado']['Receptor']['RUTRecep'] = picking.sale_id.partner_id.rut_cliente
        res['Encabezado']['Receptor']['RznSocRecep'] = picking.sale_id.partner_id.name
        res['Encabezado']['Receptor']['GiroRecep'] = picking.sale_id.partner_id.giro_cliente
        res['Encabezado']['Receptor']['DirRecep'] = picking.sale_id.partner_id.street 
        res['Encabezado']['Receptor']['CmnaRecep'] = picking.sale_id.partner_id.state_id.name
        
        if picking.carrier_id or picking.sale_id.partner_id != picking.partner_id:
            res['Encabezado']['Transporte'] = collections.OrderedDict()
        
        # Transporte
        if picking.carrier_id:
            res['Encabezado']['Transporte']['RUTTrans'] = picking.carrier_id.partner_id.rut_cliente
            if picking.patente_transporte:
                res['Encabezado']['Transporte']['Patente'] = picking.patente_transporte
            if picking.chofer_id:
                res['Encabezado']['Transporte']['Chofer'] = collections.OrderedDict()
                res['Encabezado']['Transporte']['Chofer']['RUTChofer'] = picking.chofer_id.rut_cliente
                res['Encabezado']['Transporte']['Chofer']['NombreChofer'] = picking.chofer_id.name
        
        if picking.sale_id.partner_id != picking.partner_id:
            res['Encabezado']['Transporte']['DirDest'] = picking.partner_id.street
            res['Encabezado']['Transporte']['CmnaDest'] = picking.partner_id.state_id.name
        
        res['Detalle'] = list()

        # obtener las lineas desde el pedido de venta
        lineas_venta = picking.sale_id.order_line
        for linea in lineas_venta:
            linea_dicc = collections.OrderedDict()
            if linea.product_id.default_code:
                linea_dicc['CdgItem'] = collections.OrderedDict()
                linea_dicc['CdgItem']['TpoCodigo'] = 'INT1'
                linea_dicc['CdgItem']['VlrCodigo'] = linea.product_id.default_code
            linea_dicc['NmbItem'] = linea.product_id.name_template
            linea_dicc['QtyItem'] = linea.quantity
            linea_dicc['PrcItem'] = linea.price_unit

            if linea.discount:
                linea_dicc['DescuentoPct'] = linea.discount

            res['Detalle'] += [linea_dicc]

        if not res['Detalle']:
            raise osv.except_osv("Error","El documento no contiene lineas.")
            return False

        return res

    def generar_guia(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe generar un documento a la vez.'
        dte_obj = self.pool.get('mc.dte')
        picking = self.browse(cr, uid, ids[0])
        if picking.sale_id:
            diario = picking.stock_journal_id
            if diario and diario.mc_dte_config_id and diario.sii_dte:
                dicc_u = self.generar_dicc_usuario(cr, uid, picking, context)
                dicc_d = self.generar_dicc_dte(cr, uid, picking, context)
                mc_dte_id = dte_obj.dte_sii(cr, uid, dicc_d, dicc_u, context)
                if mc_dte_id != 0:
                    self.write(cr, uid, [picking.id], {'mc_dte_id':mc_dte_id})
                    mc_dte = dte_obj.browse(cr, uid, mc_dte_id)
                    mensaje = '<b>DTE creado:</b><br>'
                    mensaje += 'Tipo: ' + str(mc_dte.codigo_sii) + '<br>'
                    mensaje += 'Folio: ' + str(mc_dte.folio_dte_sii) + '<br>'
                    mensaje += 'Track ID: ' + str(mc_dte.track_id) + '<br>'
                    self.message_post(cr, uid, [picking.id], body=tools.ustr(mensaje), context=context)
                    dte_obj.write(cr, uid, [mc_dte_id], {'picking_out_id': picking.id})
        return True
#stock_picking()
stock_picking_out()


class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'tipo_movimiento': fields.selection([
            ('1', 'Operacion constituye venta'),
            ('2', 'Ventas por efectuar'),
            ('3', 'Consignaciones'),
            ('4', 'Entrega gratuita'),
            ('5', 'Traslados internos'),
            ('6', 'Otros traslados no venta'),
            ('7', 'Guia de devolucion'),
            ('8', 'Traslado para exportacion. (no venta)'),
            ('9', 'Venta para exportacion'),
            ], 'Movimiento', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="Tipo de movimiento", select=True),
    }

    _defaults = {
        'tipo_movimiento': '1',
    }

sale_order()
