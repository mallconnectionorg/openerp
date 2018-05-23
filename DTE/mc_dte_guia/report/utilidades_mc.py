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

#import collections

from openerp.osv import osv
from bs4 import BeautifulSoup
from datetime import datetime

import logging

class mc_dte_utilidades(osv.osv):
    _inherit = 'mc.dte.utilidades'

    def traslado(self, soup):
        try:
            a = 'A ' + soup.Encabezado.Transporte.DirDest.string
            a += ', ' + soup.Encabezado.Transporte.CmnaDest.string
        except:
            a = ''
        try:
            por = ' por ' + self.rut_formato_impresion(soup.Encabezado.Transporte.RUTTrans.string.replace('.','',2))
        except:
            por = ''
        try:
            en = ' en ' + soup.Encabezado.Transporte.Patente.string
        except:
            en = ''
        try:
            chofer = ' por chofer ' + soup.Encabezado.Transporte.Chofer.NombreChofer.string
            chofer += ', R.U.T. ' + self.rut_formato_impresion(soup.Encabezado.Transporte.Chofer.RUTChofer.string.replace('.','',2))
        except:
            chofer = ''
        
        res = a + por + en + chofer
        
        return res

    def tipo_movimiento(self, soup):
        tipo_movimiento_dicc = {
            '1': 'Operacion constituye venta',
            '2': 'Ventas por efectuar',
            '3': 'Consignaciones',
            '4': 'Entrega gratuita',
            '5': 'Traslados internos',
            '6': 'Otros traslados no venta',
            '7': 'Guia de devolucion',
            '8': 'Traslado para exportacion. (no venta)',
            '9': 'Venta para exportacion',
        }
        try:
            traslado = soup.Encabezado.IdDoc.IndTraslado.string
        except:
            traslado = False
        if traslado and traslado in tipo_movimiento_dicc:
            res = tipo_movimiento_dicc[traslado]
        else:
            res = ''
        return res

    def dicc_imp_guia(self, cr, uid, pick, context=None):
        logger = logging.getLogger('dicc_imp')
        pick_obj = self.pool.get('stock.picking.out')
        pick_brw = pick_obj.browse(cr, uid, pick.id)
        dte_obj = pick_brw.mc_dte_id
        dte_config_obj = pick_brw.stock_journal_id.mc_dte_config_id
        if dte_obj.ruta and dte_obj.name:
            ruta_completa = dte_obj.ruta + dte_obj.name + '.xml'
        else:
            return dict()
        xml = ''
        with open(ruta_completa, 'r') as archivo:
            xml = archivo.read()
        soup = BeautifulSoup(xml,'xml')
        res = dict()
        res['emisor_rs'] = dte_config_obj.razonsocial
        res['emisor_giro'] = dte_config_obj.giroemisor
        res['emisor_cm'] = dte_config_obj.direccioncasamatriz
        res['emisor_suc'] = dte_config_obj.direccionorigen
        res['emisor_cont'] = dte_config_obj.infocontacto
        res['emisor_rut'] = self.rut_formato_impresion(soup.Encabezado.Emisor.RUTEmisor.string.replace('.','',2))
        res['tipo_doc'] = self.tipo_documento(cr, uid, soup.Encabezado.IdDoc.TipoDTE.string)
        res['folio'] = self.formatoNumero(soup.Encabezado.IdDoc.Folio.string)
        res['oficina_sii'] = dte_config_obj.oficinasii
        res['fecha_texto'] = self.fecha_cadena(soup.Encabezado.IdDoc.FchEmis.string)
        res['receptor_rs'] = pick_brw.sale_id.partner_id.name
        res['receptor_rut'] = self.rut_formato_impresion(soup.Encabezado.Receptor.RUTRecep.string.replace('.','',2))
        res['receptor_giro'] = pick_brw.sale_id.partner_id.giro_cliente
        direccion_comuna_receptor = self.direccion_receptor(cr, uid, pick_brw.sale_id.partner_id)
        res['receptor_direccion'] = direccion_comuna_receptor['direccion']
        res['receptor_comuna'] = direccion_comuna_receptor['comuna']
        res['cond_pago'] = pick_brw.sale_id.payment_term and pick_brw.sale_id.payment_term.name[:22] or ''
        res['detalle'] = self.lineas_detalle(xml)
        res['referencias'] = self.lineas_referencias(cr, uid, xml)
        res['comisiones'] = self.lineas_comisiones(xml)
        lineas_restar = 0
        if res['comisiones']:
            lineas_restar += 2 + len(res['comisiones'])
        if res['referencias']:
            lineas_restar += 2 + len(res['referencias'])
        lineas_detalle_relleno = 28 - lineas_restar
        if lineas_detalle_relleno < 0:
            lineas_detalle_relleno = 0
        res['lineas_detalle_relleno'] = lineas_detalle_relleno
        res['ruta_timbre'] = dte_obj.ruta + dte_obj.name + '.png'
        res['texto_resol'] = self.texto_resol(soup)
        res['cedible'] = self.cedible(soup.Encabezado.IdDoc.TipoDTE.string)
        res['documento_exento'] = self.documento_exento(soup)
        try:
            res['descuento'] = self.formatoNumero(soup.Totales.DescuentoMonto.string)
        except:
            res['descuento'] = ''
        try:
            res['monto_neto'] = self.formatoNumero(soup.Totales.MntNeto.string)
        except:
            res['monto_neto'] = ''
        try:
            res['monto_exento'] = self.formatoNumero(soup.Totales.MntExe.string)
        except:
            res['monto_exento'] = ''
        try:
            res['nombre_iva'] = 'IVA ' + soup.Totales.TasaIVA.string + '%'
            res['monto_iva'] = self.formatoNumero(soup.Totales.IVA.string)
        except:
            res['nombre_iva'] = ''
            res['monto_iva'] = ''
        res['monto_total'] = self.formatoNumero(soup.Totales.MntTotal.string)
        
        res['traslado'] = self.traslado(soup)
        
        res['tipo_movimiento'] = self.tipo_movimiento(soup)
        
        return res

mc_dte_utilidades()
