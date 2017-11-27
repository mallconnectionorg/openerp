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
from openerp import netsvc
from os import sys
from libredte.sdk import LibreDTE
from bs4 import BeautifulSoup

import base64
import unicodedata

#elimina_tildes de Victor Alvarez https://gist.github.com/victorono
def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',unicode(cadena)) if unicodedata.category(c) != 'Mn'))
    return s.decode()

class mc_dte(osv.osv):
    _name = 'mc.dte'

    _columns = {
        'name': fields.char('Nombre archivo'),
        'invoice_id': fields.many2one('account.invoice', 'Factura/Nota'),
        'codigo_sii': fields.char('Codigo DTE SII', size=16),
        'folio_dte_sii': fields.char('Folio DTE SII', size=64),
        'estado_dte': fields.char('Estado DTE', size=64),
        'track_id': fields.char('Track ID SII', size=64),
    }

    def consultar_dte(self, cliente, dicc_dte):
        datos = {
            "emisor": dicc_dte['Encabezado']['Emisor']['RUTEmisor'],
            "dte": dicc_dte['Encabezado']['IdDoc']['TipoDTE'],
            "folio": dicc_dte['Encabezado']['IdDoc']['Folio'],
            "fecha": dicc_dte['Encabezado']['IdDoc']['FchEmis'],
            "total": dicc_dte['Encabezado']['Totales']['MntTotal'],
        }
        consultar = cliente.post('/dte/dte_emitidos/consultar?getXML=0', datos)
        if consultar.status_code!=200 :
            error_dte = elimina_tildes(consultar.json())
            raise osv.except_osv( 'Error!',
            "No se pudo emitir el DTE. Error: %s"%error_dte)
            return False
        else:
            return consultar.json()

    def emitir_dte(self, cliente, dicc_dte):
        emitir = cliente.post('/dte/documentos/emitir', dicc_dte)
        if emitir.status_code!=200 :
            error_dte = elimina_tildes(emitir.json())
            raise osv.except_osv( 'Error!',
            "No se pudo emitir el DTE. Error: %s"%error_dte)
            return False
        else:
            return emitir

    def generar_dte(self, cliente, emitir):
        generar = cliente.post('/dte/documentos/generar', emitir.json())
        if generar.status_code!=200 :
            error_dte = elimina_tildes(generar.json())
            raise osv.except_osv( 'Error!',
            "No se pudo generar el DTE. Error: %s"%error_dte)
            return False, False, False
        else:
            dte = str(generar.json()['dte'])
            folio = str(generar.json()['folio'])
            emisor = str(emitir['emisor'])
            return dte, folio, emisor

    def xml_dte(self, cliente, dte, folio, emisor):
        obtener_xml = cliente.get('/dte/dte_emitidos/xml/'+dte+'/'+folio+'/'+emisor)
        if obtener_xml.status_code!=200:
            error_dte = elimina_tildes(obtener_xml.json())
            raise osv.except_osv('Error!',
            "No se pudo obtener el XML del DTE. Error: %s"%error_dte)
            return False
        else:
            xml = base64.b64decode(obtener_xml.json())
            return xml

    def ted_dte(self, cliente, dte, folio, emisor):
        obtener_ted = cliente.get('/dte/dte_emitidos/ted/'+dte+'/'+folio+'/'+emisor)
        if obtener_ted.status_code!=200 :
            error_dte = elimina_tildes(obtener_ted.json())
            raise osv.except_osv( 'Error!',
            "No se pudo obtener el TED del DTE. Error: %s"%error_dte)
            return False
        else:
            return obtener_ted.content

    def guardar_archivos(self, xml, ted, ruta):
        with open(ruta+'.xml', 'wb') as fx:
            fx.write(xml)
        with open(ruta+'.png', 'wb') as fp:
            fp.write(ted)
        return True

    def chequear_existencia(self, cliente_ws, dicc_dte):
        emisor = dicc_dte['Encabezado']['Emisor']['RUTEmisor']
        folio = dicc_dte['Encabezado']['IdDoc']['Folio']
        dte = dicc_dte['Encabezado']['IdDoc']['TipoDTE']
        res = False
        mensaje = ''
        dicc_res = dict()
        try:
            # se obtiene primero el xml del servidor para ver si existe.
            # si existe se verifica que contenga otros datos o los mismos
            # Fecha, Cliente, Monto
            obtener_xml = cliente_ws.get('/dte/dte_emitidos/xml/'+dte+'/'+folio+'/'+emisor)
            if obtener_xml.status_code != 200:
                return False, 'No existe', dict()
            else:
                res = True
                
                fecha_dicc = dicc_dte['Encabezado']['IdDoc']['FchEmis']
                cliente_dicc = dicc_dte['Encabezado']['Receptor']['RUTRecep']
                monto_dicc = dicc_dte['Encabezado']['Totales']['MntTotal']
                
                xml = base64.b64decode(obtener_xml.json())
                soup = BeautifulSoup(xml,'xml')
                cliente_dte = soup.Encabezado.Receptor.RUTRecep.string
                fecha = soup.Encabezado.IdDoc.FchEmis.string
                monto_total = soup.Encabezado.Totales.MntTotal.string
                
                # comparar xml dicc
                iguales = True
                if cliente_dte != cliente_dicc:
                    iguales = False
                if fecha != fecha_dicc:
                    iguales = False
                if monto_total != monto_dicc:
                    iguales = False
                if iguales:
                    mensaje = 'Existe uno igual'
                    dicc_res['emisor'] = emisor
                    dicc_res['dte'] = dte
                    dicc_res['folio'] = folio
                else:
                    mensaje = 'Existe uno distinto'
                    dicc_res['emisor'] = emisor
                    dicc_res['dte'] = dte
                    dicc_res['folio'] = folio
                    dicc_res['cliente_dte'] = cliente_dte
                    dicc_res['fecha_dte'] = fecha
                    dicc_res['monto_total'] = monto_total
        except:
            return False, 'No existe', dict()
        return res, mensaje, dicc_res

    def quitar_folio(self, dicc_dte):
        del dicc_dte['Encabezado']['IdDoc']['Folio']
        folio = dicc_dte['Encabezado']['IdDoc'].get('Folio', False)
        if folio:
            raise osv.except_osv("Error","No se pudo eliminar la clave Folio")
            return False
        return dicc_dte

    def dte_sii(self, dicc_dte={}, dicc_usuario={},context=None):
        # el dicc_dte es un diccionario de python que debe cumplir con las
        # especificaciones de https://github.com/LibreDTE/libredte-lib/tree/master/examples/json
        # hay un ejemplo contenido en este modulo en examples/ejemplo.json
        
        # dicc_usuario es un diccionario que debe contener lo siguiente:
        # servidor de LibreDTE
        # hash de usuario en el servidor de LibreDTE
        # tipo_dte esta clave se usa para identificar el objeto del cual
        # proviene y determinara su tipo (picking, invoice, pos order)
        # ruta_arvchivos, pruebas y otra informacion que este establecida
        # en el objeto sale.shop
        if dicc_dte and dicc_usuario:

            servidor = dicc_usuario['servidor']
            hash_dte = dicc_usuario['hash_dte']
            tipo_dte = dicc_usuario['tipo_dte'] #picking_id, invoice_id, posorder_id // Nombre del campo
            id_externo = int(dicc_usuario['id_externo']) #picking_id, invoice_id, posorder_id // ID objeto externo
            ruta_archivos = dicc_usuario['ruta_archivos'] or False
            pruebas = dicc_usuario['dte_pruebas']
            enviar_num_folio = dicc_usuario['enviar_num_folio']

            if not ruta_archivos:
                raise osv.except_osv("Error","No hay ruta donde guardar los archivos")
                return False

            Cliente = LibreDTE(hash_dte, servidor)

            if not enviar_num_folio:
                # quitar numero de folio del dicionario dte
                dicc_dte = self.quitar_folio(dicc_dte)
                existe_dte = False
            else:
                existe_dte, mensaje_existe, dicc_cheq = self.chequear_existencia(Cliente, dicc_dte)
            
            if existe_dte:
                if mensaje_existe == 'Existe uno igual':
                    dte = dicc_cheq.get('dte', False)
                    folio = dicc_cheq.get('folio', False)
                    emisor = dicc_cheq.get('emisor', False)
                    # si ya se sabe que hay uno igual en base al xml se
                    # debe verificar que se haya enviado al SII, que
                    # tenga track ID y además el estado
                elif mensaje_existe == 'Existe uno distinto':
                    dte = dicc_cheq.get('dte', False)
                    folio = dicc_cheq.get('folio', False)
                    emisor = dicc_cheq.get('emisor', False)
                    cliente_dte = dicc_cheq.get('cliente', False)
                    fecha_dte = dicc_cheq.get('fecha_dte', False)
                    monto_total = dicc_cheq.get('emisor', False)
                    error_dte = '\nFolio: '+str(folio)+'\n'
                    error_dte += 'DTE: '+str(dte)+'\n'
                    error_dte += 'Emisor: '+str(emisor)+'\n'
                    error_dte += 'Cliente: '+str(cliente_dte)+'\n'
                    error_dte += 'Monto Total: '+str(monto_total)+'\n'
                    raise osv.except_osv( 'Error!',
                    "El DTE ya existe, pero con otros datos. Error: %s"%error_dte)
                    return False

                if pruebas:
                    return True
            else:
                # crear DTE temporal
                emitir = self.emitir_dte(Cliente, dicc_dte)

                # se ejecuta hasta aca si esta en modo de pruebas
                if pruebas:
                    return True

                # crear DTE real
                dte, folio, emisor = self.generar_dte(Cliente, emitir)

            if dte and folio and emisor:
                nombre_archivo = emisor + '_' + dte + '_' + folio
                ruta_completa = ruta_archivos + nombre_archivo
            else:
                ruta_completa = False
                raise osv.except_osv("Error","No se pudo generar el DTE.")
                return False

            # obtener el XML del DTE
            xml = self.xml_dte(Cliente, dte, folio, emisor)

            #obtener el TED del DTE
            ted = self.ted_dte(Cliente, dte, folio, emisor)

            # guardar archivos XML y TED
            self.guardar_archivos(xml, ted, ruta_completa)

            # crear un mc.dte con los datos obtenidos, pero primero buscar para ver si ya existe
            #mdo = self.pool.get()
            filtro = [(tipo_dte,'=',id_externo)]
            filtro += [('folio_dte_sii','=',folio)]
            filtro += [('codigo_sii','=',dte)]
            mc_dte_ids = self.search(cr, uid, filtro)
            if not mc_dte_ids:
                consulta = self.consultar_dte(Cliente, dicc_dte)
                create_vals = dict()
                create_vals['name'] = nombre_archivo
                create_vals['codigo_sii'] = dte
                create_vals['folio_dte_sii'] = folio
                create_vals['estado_dte'] = consulta['revision_estado']
                create_vals['track_id'] = consulta['track_id']
                create_vals[tipo_dte] = id_externo
                self.create(cr, uid, create_vals)
            elif mc_dte_ids and len(mc_dte_ids) == 1:
                consulta = self.consultar_dte(Cliente, dicc_dte)
                # escribir / actualizar
                write_vals = dict()
                write_vals['estado_dte'] = consulta['revision_estado']
                write_vals['track_id'] = consulta['track_id']
                self.write(cr, uid, mc_dte_ids, write_vals)
            else:
                raise osv.except_osv("Error","Hay mas de un registro (mc.dte) para este DTE.")
                return False

        return True

    def generar_pdf(self, ted, xml):
        res = ''
        return res

mc_dte()

class mc_tipo_dte(osv.osv):
    _name = 'mc.tipo.dte'
    _columns = {
        'codigo_sii': fields.char('Codigo SII'),
        'name': fields.char('Nombre'),
    }
mc_tipo_dte()

class sale_shop(osv.osv):
    """En OpenERP 7 se heredara del objeto sale.shop, pero en Odoo 8
    se debera crear un objeto que lo reemplace ya que en esa version no
    existe sale.shop.
    """

    texto_folio = """Al seleccionar esta opcion se enviara el numero de folio por este sistema, de lo contrario se usara el entregado por LibreDTE."""

    texto_ruta = """Esta es la ruta en su servidor que usara para guardar los archivos XML y PNG. Debe terminar en una barra inclinada (/)."""

    texto_pruebas = """Seleccione esta opcion si solo esta realizando pruebas y aun no genera DTE reales."""

    _inherit = 'sale.shop'
    _columns = {
        'servidor_dte': fields.char('Servidor DTE'),
        'sucursal_sii': fields.char('Sucursal SII'),
        'ruta_archivos': fields.char('Ruta archivos', help=texto_ruta),
        'dte_permitidos': fields.many2many('mc.tipo.dte', 'dte_permitido_rel', 'shop_id', 'dte_id', 'DTE permitidos'),
        'hash_tienda': fields.char('Hash Tienda'),
        'dte_pruebas': fields.boolean('Pruebas',help=texto_pruebas),
        'enviar_num_folio': fields.boolean('Enviar numero de folio',help=texto_folio),
    }

sale_shop()
