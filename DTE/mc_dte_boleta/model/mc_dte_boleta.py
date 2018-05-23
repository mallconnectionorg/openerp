#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   DTE Chile OpenERP 7
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
from openerp import tools, SUPERUSER_ID
#from libredte.sdk import LibreDTE
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
        'posorder_id': fields.many2one('pos.order', 'Boleta', readonly=True),
    }

    #def dte_sii(self, cr, uid, dicc_dte={}, dicc_usuario={},context=None):
    #    res = super(mc_dte, self).dte_sii(cr, uid, dicc_dte, dicc_usuario,context=context)
    #    return res

mc_dte()

class mc_dte_config(osv.osv):
    _inherit = 'mc.dte.config'

    _columns = {
        'web_boletas': fields.char('Web Boletas'),
    }

mc_dte_config()

class pos_order(osv.osv):
    _inherit = 'pos.order'

    def _default_partner(self, cr, uid, context=None):
        po = self.pool.get('res.partner')
        partner_ids = po.search(cr, uid, [('name','=','Boleta')], context=context)
        return partner_ids and partner_ids[0] or False

    _columns = {
        'mc_dte_id': fields.many2one('mc.dte', 'Registro DTE', readonly=True),
        'devolucion_cambio': fields.boolean('Devolucion/Cambio'),
        'dte_procesado': fields.boolean('DTE procesado'),
        'numero_boleta': fields.char('N° bol.', size=64, readonly=True),
    }

    _defaults = {
        'devolucion_cambio': False,
        'dte_procesado': False,
        'partner_id': _default_partner,
    }

    def refund(self, cr, uid, ids, context=None):
        res = super(pos_order, self).refund(cr, uid, ids, context=context)
        return res

    def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
        res = super(pos_order, self).onchange_partner_id(cr, uid, ids, part=part, context=context)
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        logger = logging.getLogger('copy_boleta')
        if not default:
            default = {}
        d = dict()
        d['numero_boleta'] = False
        d.update(default)
        logger.warn(d)
        return super(pos_order, self).copy(cr, uid, id, d, context=context)

    def create(self, cr, uid, values, context=None):
        logger = logging.getLogger('create_boleta')
        #nombre_codigo = self.codigo_secuencia(cr, uid, values)
        #devolucion = False
        #if 'name' in values:
        #    if 'REFUND' in values['name']:
        #        devolucion = True
        #if nombre_codigo and not devolucion:
        #    values['numero_boleta'] = self.pool.get('ir.sequence').get(cr, uid, nombre_codigo)
        logger.warn(values)
        return super(pos_order, self).create(cr, uid, values, context=context)

    #def action_paid(self, cr, uid, ids, context=None):
    #    res = super(pos_order, self).action_paid(cr, uid, ids, context=context)
    #    self.dte_boleta(cr, uid, ids, context=context)
    #    return res

    def refacturar(self, cr, uid, ids, context=None):
        msj_a = 'Debe realizar esta acción sólo para un pedido de venta'
        msj_a += ' a la vez.'
        assert len(ids) == 1, msj_a
        pedido = self.browse(cr, uid, ids[0])
        if pedido.state == 'invoiced':
            rvals = dict()
            inv_id = pedido.invoice_id
            if not inv_id:
                rvals['state'] = 'paid'
                rvals['dte_procesado'] = False
            elif inv_id.state == 'draft' and inv_id.internal_number:
                rvals['state'] = 'paid'
                rvals['dte_procesado'] = False
            elif inv_id.state == 'draft' and not inv_id.internal_number:
                adv = "Advertencia"
                msj = "Tiene una factura o nota asociada que esta en "
                msj += "estado Borrador. Puede continuar editandola."
                raise osv.except_osv(adv, msj)
                return False
            elif inv_id.state == 'cancel':
                adv = "Advertencia"
                msj = "Tiene una factura o nota asociada que esta en "
                msj += "estado Cancelado. Puede dejarla en borrador y "
                msj += "editarla nuevamente."
                raise osv.except_osv(adv, msj)
                return False
            else:
                return True
            if rvals:
                self.write(cr, uid, [pedido.id], rvals, context=context)
        return True

    def codigo_secuencia(self, cr, uid, diario):
        nombre_codigo = 'boleta.electronica.' + diario.sii_dte
        return nombre_codigo

    def actualizar_pedido(self, cr, uid, pedido, context=None):
        diario = pedido.sale_journal
        if not diario.mc_dte_config_id.enviar_num_folio:
            return pedido
        else:
            nombre_codigo = self.codigo_secuencia(cr, uid, diario)
        if not pedido.numero_boleta:
            # esto es necesario para pasar el numero de folio a
            # LibreDTE, pero si falla la generacion del DTE el folio
            # queda tomado, pero sin DTE asociado. 
            # ¿como podriamos mejorar esto?
            wval = dict()
            wval['numero_boleta'] = self.pool.get('ir.sequence').get(cr, uid, nombre_codigo)
            self.write(cr, uid, [pedido.id], wval)
        pedido = self.browse(cr, uid, pedido.id)
        return pedido

    def boleta_factura_nota(self, cr, uid, ids, context=None):
        for pedido in self.browse(cr, uid, ids, context=context):
            if pedido.dte_procesado:
                return True
            dc = pedido.devolucion_cambio
            diario = pedido.sale_journal
            if diario.mc_dte_config_id and diario.sii_dte:
                if diario.sii_dte in ['39','41'] and not dc:
                    return self.dte_boleta(cr, uid, pedido, context=context)
                elif diario.sii_dte in ['33','34'] and not dc:
                    return super(pos_order, self).action_invoice(cr, uid, [pedido.id], context=context)
                elif diario.sii_dte in ['33','34','39','41'] and dc:
                    return self.nota_tpv(cr, uid, [pedido.id], context=context)
        return True

    def action_invoice(self, cr, uid, ids, context=None):
        res = super(pos_order, self).action_invoice(cr, uid, ids, context=context)
        wvals = dict()
        wvals['dte_procesado'] = True
        self.write(cr, uid, ids, wvals)
        return res

    def nota_tpv(self, cr, uid, ids, context=None):
        # buscar diario de nota de credito electronica
        diarios_ids = self.pool.get('account.journal').search(cr, uid, [('sii_dte','=','61')])
        if diarios_ids and len(diarios_ids) == 1 and len(ids) == 1:
            pedido = self.browse(cr, uid, ids[0])
            inv_obj = self.pool.get('account.invoice')
            inv_line_obj = self.pool.get('account.invoice.line')
            if pedido.partner_id.property_account_receivable:
                acc = pedido.partner_id.property_account_receivable.id
            else:
                acc = False
            inv_args = {
                'name': pedido.name,
                'origin': pedido.name,
                'account_id': acc,
                'journal_id': diarios_ids and diarios_ids[0] or None,
                'type': 'out_refund',
                'reference': pedido.name,
                'partner_id': pedido.partner_id.id,
                'comment': pedido.note or '',
                'currency_id': pedido.pricelist_id.currency_id.id,
            }
            inv_id = inv_obj.create(cr, uid, inv_args, context=context)
            wvals = dict()
            wvals['invoice_id'] = inv_id
            wvals['state'] = 'invoiced'
            wvals['dte_procesado'] = True
            self.write(cr, uid, [pedido.id], wvals, context=context)
            for linea in pedido.lines:
                inv_linea = dict()
                inv_linea['invoice_id'] = inv_id
                inv_linea['product_id'] = linea.product_id.id
                inv_linea['quantity'] = linea.qty * -1
                inv_linea['price_unit'] = linea.price_unit
                inv_linea['discount'] = linea.discount
                inv_linea['name'] = linea.product_id.default_code
                inv_linea['uos_id'] = linea.product_id.uom_id.id
                inv_linea['invoice_line_tax_id'] = [(6, 0, [x.id for x in linea.product_id.taxes_id] )]
                inv_line_obj.create(cr, uid, inv_linea, context=context)
            mod_obj = self.pool.get('ir.model.data')
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            res_id = res and res[1] or False
            return {
                'name': 'Nota de Credito',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.invoice',
                'context': "{'type':'out_refund'}",
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': inv_id or False,
            }
        return True

    def generar_dicc_usuario(self, cr, uid, pos, context=None):
        diario_id = pos.sale_journal
        res = collections.OrderedDict()
        res['servidor'] = diario_id.mc_dte_config_id.servidor_dte
        res['sucursal_sii'] = diario_id.mc_dte_config_id.sucursal_sii
        res['ruta_archivos'] = diario_id.mc_dte_config_id.ruta_archivos
        res['dte_permitidos'] = [dpe.codigo_sii for dpe in diario_id.mc_dte_config_id.dte_permitidos]
        res['hash_dte'] = diario_id.mc_dte_config_id.hash_tienda
        res['dte_pruebas'] = diario_id.mc_dte_config_id.dte_pruebas
        res['enviar_num_folio'] = diario_id.mc_dte_config_id.enviar_num_folio
        res['tipo_dte'] = 'posorder_id'
        res['id_externo'] = pos.id
        return res

    def generar_dicc_dte(self, cr, uid, pos, context=None):
        diario_id = pos.sale_journal
        res = collections.OrderedDict()
        res['Encabezado'] = collections.OrderedDict()
        res['Encabezado']['IdDoc'] = collections.OrderedDict()
        res['Encabezado']['Emisor'] = collections.OrderedDict()
        res['Encabezado']['Receptor'] = collections.OrderedDict()
        res['Encabezado']['IdDoc']['TipoDTE'] = diario_id.sii_dte
        try:
            res['Encabezado']['IdDoc']['Folio'] = int(pos.numero_boleta)
        except Exception:
            pass
        res['Encabezado']['Emisor']['RUTEmisor'] = diario_id.mc_dte_config_id.rutemisor
        if pos.partner_id:
            res['Encabezado']['Receptor']['RUTRecep'] = pos.partner_id.rut_cliente
            res['Encabezado']['Receptor']['RznSocRecep'] = pos.partner_id.name
        else:
            res['Encabezado']['Receptor']['RUTRecep'] = '66666666-6'
        res['Detalle'] = list()
        for linea in pos.lines:
            linea_dicc = collections.OrderedDict()
            if linea.product_id.default_code:
                linea_dicc['CdgItem'] = collections.OrderedDict()
                linea_dicc['CdgItem']['TpoCodigo'] = 'INT1'
                linea_dicc['CdgItem']['VlrCodigo'] = linea.product_id.default_code
            linea_dicc['NmbItem'] = linea.product_id.name
            linea_dicc['QtyItem'] = linea.qty
            linea_dicc['PrcItem'] = linea.price_subtotal_incl

            if linea.discount:
                linea_dicc['DescuentoPct'] = linea.discount

            res['Detalle'] += [linea_dicc]

        if not res['Detalle']:
            raise osv.except_osv("Error","El documento no contiene lineas.")
            return False

        return res

    def reimprimir_pos(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe imprimir un documento a la vez.'
        res = dict()
        datas = dict()
        pos = self.browse(cr, uid, ids[0])
        if not pos.mc_dte_id:
            return True
        if pos.numero_boleta:
            if pos.sale_journal.reporte_dte_id:
                report_name = pos.sale_journal.reporte_dte_id.report_name
            else:
                report_name = 'boleta.electronica.webkit'
            datas['ids'] = [pos.id]
            datas['model'] = 'pos.order'
            datas['form'] = self.read(cr, uid, pos.id, context=context)
        elif pos.invoice_id:
            if pos.invoice_id.journal_id.reporte_dte_id:
                report_name = pos.invoice_id.journal_id.reporte_dte_id.report_name
            else:
                report_name = 'factura.nota.termica.webkit'
            ai_obj = self.pool.get('account.invoice')
            datas['ids'] = [pos.invoice_id.id]
            datas['model'] = 'account.invoice'
            datas['form'] = ai_obj.read(cr, uid, pos.invoice_id.id, context=context)
        else:
            report_name = False
        if report_name and datas:
            res['type'] = 'ir.actions.report.xml'
            res['report_name'] = report_name
            res['datas'] = datas
            res['nodestroy'] = True
        return res

    def imprime_boleta(self, cr, uid, pos, context=None):
        if pos.sale_journal.reporte_dte_id:
            report_name = pos.sale_journal.reporte_dte_id.report_name
        else:
            report_name = 'boleta.electronica.webkit'
        if not pos.mc_dte_id:
            return True
        res = dict()
        datas = dict()
        datas['ids'] = [pos.id]
        datas['model'] = 'pos.order'
        datas['form'] = self.read(cr, uid, pos.id, context=context)
        res['type'] = 'ir.actions.report.xml'
        res['report_name'] = report_name
        res['datas'] = datas
        res['nodestroy'] = True
        return res

    def obtener_numero_boleta(self, cr, uid, dte_obj, dte_id):
        dte = dte_obj.browse(cr, uid, dte_id)
        if dte.folio_dte_sii:
            res = dte.folio_dte_sii
        else:
            res = False
        return res

    def dte_boleta(self, cr, uid, pos, context=None):
        pos = self.actualizar_pedido(cr, uid, pos, context=context)
        dte_obj = self.pool.get('mc.dte')
        dicc_u = self.generar_dicc_usuario(cr, uid, pos, context)
        dicc_d = self.generar_dicc_dte(cr, uid, pos, context)
        mc_dte_id = dte_obj.dte_sii(cr, uid, dicc_d, dicc_u, context)
        if mc_dte_id != 0:
            wvals = dict()
            wvals['mc_dte_id'] = mc_dte_id
            wvals['dte_procesado'] = True
            
            # si se genero el DTE, pero no se paso el numero de folio
            # hay que obtenerlo y escribirlo en el POS
            if not pos.numero_boleta:
                num_bol = self.obtener_numero_boleta(cr, uid, dte_obj, mc_dte_id)
                if num_bol:
                    wvals['numero_boleta'] = num_bol
            
            self.write(cr, uid, [pos.id], wvals)
            
            # actualizar el DTE
            dte_obj.write(cr, uid, [mc_dte_id], {'posorder_id': pos.id})
            
            # finalizar en la impresion del documento
            self.imprime_boleta(cr, uid, pos, context=context)
            
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            if vals['state'] == 'paid':
                assert len(ids) == 1, 'Debe pagar un pedido a la vez.'
                total = self.browse(cr, uid, ids[0]).amount_total
                if total < 0.0:
                    vals['devolucion_cambio'] = True
        res = super(pos_order, self).write(cr, uid, ids, vals, context=context)
        return res

pos_order()

class res_partner(osv.osv):
    _inherit = "res.partner"

    def write(self, cr, uid, ids, vals, context=None):
        logger = logging.getLogger('write res_partner')
        logger.warn('se ejecuta')
        logger.warn(vals)
        editar_ok = True
        if 'rut_cliente' in vals.keys():
            if self.formato_rut(vals['rut_cliente']) == '666666666':
                if uid != SUPERUSER_ID:
                    editar_ok = False
        for rp in self.browse(cr, uid, ids):
            if rp.rut_cliente == '66666666-6':
                if uid != SUPERUSER_ID:
                    editar_ok = False
        if not editar_ok:
            raise osv.except_osv('Error', u'Sólo el administrador puede editar al cliente Boleta.')
            return False
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, user, values, context=None):
        if 'rut_cliente' in values.keys():
            if self.formato_rut(values['rut_cliente']) == '666666666':
                sval = [('rut_cliente','=','66666666-6')]
                cliente_ids = self.search(cr, uid, sval)
                if cliente_ids:
                    raise osv.except_osv('Error', u'Ya existe el cliente Boleta.')
                    return False
        res = super(res_partner, self).create(cr, user, values, context=context)
        return res
