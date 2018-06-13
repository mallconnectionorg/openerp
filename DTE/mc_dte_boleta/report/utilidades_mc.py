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

class mc_dte_utilidades_boleta(osv.osv):
    _name = 'mc.dte.utilidades.boleta'

    def diadelasemana(self, fecha_texto):
        fecha_fecha = datetime.strptime(fecha_texto,'%Y-%m-%d')
        dia_fecha = fecha_fecha.weekday()
        if dia_fecha == 0:
            res = u'Lunes'
        elif dia_fecha == 1:
            res = u'Martes'
        elif dia_fecha == 2:
            res = u'Miércoles'
        elif dia_fecha == 3:
            res = u'Jueves'
        elif dia_fecha == 4:
            res = u'Viernes'
        elif dia_fecha == 5:
            res = u'Sábado'
        elif dia_fecha == 6:
            res = u'Domingo'
        else:
            res = ''
        return res

    def mes_texto(self, mes):
        if mes:
            if mes == '01':
                res = 'Enero'
            elif mes == '02':
                res = 'Febrero'
            elif mes == '03':
                res = 'Marzo'
            elif mes == '04':
                res = 'Abril'
            elif mes == '05':
                res = 'Mayo'
            elif mes == '06':
                res = 'Junio'
            elif mes == '07':
                res = 'Julio'
            elif mes == '08':
                res = 'Agosto'
            elif mes == '09':
                res = 'Septiembre'
            elif mes == '10':
                res = 'Octubre'
            elif mes == '11':
                res = 'Noviembre'
            elif mes == '12':
                res = 'Diciembre'
            else:
                res = ''
            return res
        else:
            res = ''
            return res

    def fecha_cadena(self, fecha_texto):
        try:
            fecha_lista = fecha_texto.split('-')
            dia = fecha_lista[2]
            mes = fecha_lista[1]
            anio = fecha_lista[0]
            nombre_dia = self.diadelasemana(fecha_texto)
            nombre_mes = self.mes_texto(mes)
            res = nombre_dia + ', ' + dia + ' de ' + nombre_mes + ' de ' + anio
        except:
            res = ''
        return res

    def formatoFechaRef(self, fecha_texto):
        try:
            fecha_texto = fecha_texto.split('-')
            dia = fecha_texto[2]
            mes = fecha_texto[1]
            anio = fecha_texto[0]
            res = dia + '-' + mes + '-' + anio
        except:
            res = ''
        return res

    def formatoNumero(self, numero):
        numero = str(numero)
        nn = ''
        negativo = False
        if '-' in numero:
            negativo = True
            numero = str(abs(float(numero)))
        largo_cadena = float(len(numero))
        if largo_cadena % 3 == 0:
            rango = int(largo_cadena / 3)
        else:
            rango = int(largo_cadena / 3) + 1
        for i in range(rango):
            if len(numero) >= 3:
                if nn == '':
                    nn += numero[-3:]
                else:
                    nn = numero[-3:] + '.' + nn
                numero = numero[:-3]
            else:
                if nn:
                    nn = numero + '.' + nn
                else:
                    nn = numero
        if nn:
            if negativo:
                nn = '-' + nn
            res = nn
        else:
            res = numero
        return res

    def rut_formato_impresion(self, rut):
        rut = rut.split('-')
        dv = rut[1]
        rut = rut[0]
        rut = self.formatoNumero(rut)
        rut = rut + '-' + dv
        return rut

    def tipo_documento(self, cr, uid, cod_sii):
        mtd_obj = self.pool.get('mc.tipo.dte')
        mtd_ids = mtd_obj.search(cr, uid, [('codigo_sii','=',cod_sii)])
        res = ''
        if mtd_ids and len(mtd_ids) == 1:
            res = mtd_obj.browse(cr, uid, mtd_ids[0]).name.upper()
        return res

    def direccion_receptor(self, cr, uid, partner):
        res = dict()
        calle1 = partner.street
        calle2 = partner.street2
        ciudad = partner.city
        res['direccion'] = calle1 or '' + ' ' + calle2 or '' + ', ' + ciudad or ''
        res['comuna'] = partner.state_id and partner.state_id.name or ''
        return res

    def lineas_detalle(self, xml):
        res = []
        soup = BeautifulSoup(xml,'xml')
        Documento = soup.find('Documento')
        for detalle in Documento.findChildren('Detalle'):
            # codigo = ''
            # descripcion = detalle.NmbItem.string
            try:
                codigo = detalle.CdgItem.VlrCodigo.string
            except:
                codigo = ''
            try:
                descripcion = detalle.DscItem.string
            except:
                descripcion = ''
            try:
                descuento = detalle.DescuentoMonto.string
            except:
                descuento = '0'
            dicc_tmp = dict()
            dicc_tmp['codigo'] = codigo
            dicc_tmp['descripcion'] = descripcion
            dicc_tmp['nombre'] = detalle.NmbItem.string
            dicc_tmp['cantidad'] = detalle.QtyItem.string
            dicc_tmp['precio_unitario'] = self.formatoNumero(detalle.PrcItem.string)
            dicc_tmp['descuento'] = descuento
            dicc_tmp['valor'] = self.formatoNumero(detalle.MontoItem.string)
            dicc_tmp['unidad'] = 'Uni'
            res += [dicc_tmp]
        return res

    def lineas_referencias(self, cr, uid, xml):
        res = []
        soup = BeautifulSoup(xml,'xml')
        Documento = soup.find('Documento')
        for referencia in Documento.findChildren('Referencia'):
            dicc_tmp = dict()
            dicc_tmp['tipo_documento'] = self.tipo_documento(cr, uid, referencia.TpoDocRef.string)
            dicc_tmp['folio_ref'] = referencia.FolioRef.string
            dicc_tmp['fecha_ref'] = self.formatoFechaRef(referencia.FchRef.string)
            dicc_tmp['razon_ref'] = referencia.RazonRef.string
            res += [dicc_tmp]
        return res

    def lineas_comisiones(self, xml):
        res = dict()
        soup = BeautifulSoup(xml,'xml')
        Documento = soup.find('Documento')
        lista_temp = list()
        for comision in Documento.findChildren('Comision'):
            dicc_temp = dict()
            dicc_tmp['glosa'] = comision.Glosa.string
            dicc_tmp['iva'] = comision.ValComIVA.string
            dicc_tmp['neto'] = comision.ValComNeto.string
            dicc_tmp['exento'] = comision.ValComExe.string
            lista_temp += [dicc_tmp]
        dicc_tot = dict()
        for totales_comisiones in Documento.findChildren('Totales'):
            try:
                dicc_tot['suma_neto'] = totales_comisiones.ValComNeto.string
                dicc_tot['suma_exento'] = totales_comisiones.ValComExe.string
                #dicc_tot['suma_iva'] = totales_comisiones.ValComIVA.string
            except:
                return res
        if dicc_tot and lista_temp:
            res['totales'] = dicc_tot
            res['lineas'] = lista_temp
        return res

    def cedible(self, cod_sii_dte):
        res = ''
        if cod_sii_dte == '52':
            res = 'CEDIBLE CON SU FACTURA'
        if cod_sii_dte in ['33','34','43','46']:
            res = 'CEDIBLE'
        # descomentar la siguiente linea para pruebas de impresion
        #res = 'CEDIBLE'
        return res

    def documento_exento(self, soup):
        cod_dte = soup.Encabezado.IdDoc.TipoDTE.string
        if cod_dte == '41':
            return 'EXENTO'
        else:
            return ''

    def texto_resol(self, soup):
        FchResol = soup.Caratula.FchResol.string
        NroResol = soup.Caratula.NroResol.string
        fecha_lista = FchResol.split('-')
        anio = fecha_lista[0]
        res = NroResol + ' de ' + anio
        return res

    def dicc_imp(self, cr, uid, pos, context=None):
        logger = logging.getLogger('dicc_imp')
        pos_obj = self.pool.get('pos.order')
        pos_brw = pos_obj.browse(cr, uid, pos.id)
        dte_obj = pos_brw.mc_dte_id
        dte_config_obj = pos.sale_journal.mc_dte_config_id
        ruta_completa = dte_obj.ruta + dte_obj.name + '.xml'
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
        res['receptor_rs'] = pos_brw.partner_id.name
        res['receptor_rut'] = self.rut_formato_impresion(soup.Encabezado.Receptor.RUTRecep.string.replace('.','',2))
        res['detalle'] = self.lineas_detalle(xml)
        res['ruta_timbre'] = dte_obj.ruta + dte_obj.name + '.png'
        res['texto_resol'] = self.texto_resol(soup)
        res['documento_exento'] = self.documento_exento(soup)
        res['notas'] = pos_brw.note or ''
        res['ref_pos'] = pos_brw.name
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
        return res

mc_dte_utilidades_boleta()
