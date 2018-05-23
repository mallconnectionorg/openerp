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

class account_journal(osv.osv):
    _inherit = "account.journal"

    _columns = {
        'sii_dte': fields.char('Codigo DTE SII', size=8),
        'mc_dte_config_id': fields.many2one('mc.dte.config', 'Configuracion DTE'),
        'reporte_dte_id': fields.many2one('ir.actions.report.xml', 'Reporte DTE'),
    }

account_journal()

class res_partner(osv.osv):
    _inherit = "res.partner"

    def formato_rut(self, rut):
        if rut:
            rut = rut.replace('-','',1).replace('.','',2)
            if type(rut) != type(1):
                rut = rut.upper()
        return rut

    def check_rut(self, rut):
        if not rut:
            return True
        lstmp = []
        di = 1
        while di < 10:
            if di != 6:
                dstr = """%s%s%s%s%s%s%s%s%s"""%(di,di,di,di,di,di,di,di,di)
                lstmp.append(dstr)
            di += 1
        if rut in lstmp:
            return False
        if len(rut) != 9:
            if len(rut) != 8:
                return False
        try:
            int(rut[:-1])
        except:
            return False
        dv = rut[-1]
        rut = rut[:-1]
        x = 9
        s = 0
        for i in range(len(rut)-1,-1,-1):
            if x < 4:
                x = 9
            s += int(rut[i]) * x
            x -= 1
        if dv == 'k' or dv == 'K':
            if s%11 == 10:
                return True
            else:
                return False
        if str(s%11) == dv:
            return True
        else:
            return False 
        return False

    def rut_formato_guardar(self, rut):
        if rut:
            if type(rut) == type(1):
                rut = str(rut)
            dv = rut[-1]
            rut = rut[:-1]
            rut = '{0}{1}{2}'.format(rut, '-', dv)
            rut = rut.upper()
        return rut

    _columns = {
        'rut_cliente': fields.char('RUT', size=18),
        'giro_cliente': fields.char('Giro', size=96),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'rut_cliente' in vals.keys():
            rut = self.formato_rut(vals['rut_cliente'])
            rut_ok = self.check_rut(rut)
            if rut_ok:
                vals['rut_cliente'] = self.rut_formato_guardar(rut)
            else:
                raise osv.except_osv('Error', u'El RUT no es válido.')
                return False
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, user, values, context=None):
        if 'rut_cliente' in values.keys():
            rut = self.formato_rut(values['rut_cliente'])
            rut_ok = self.check_rut(rut)
            if rut_ok:
                values['rut_cliente'] = self.rut_formato_guardar(rut)
            else:
                raise osv.except_osv('Error', u'El RUT no es válido.')
                return False
        res = super(res_partner, self).create(cr, user, values, context=context)
        return res

class mc_dte(osv.osv):
    _name = 'mc.dte'
    _order = 'id desc'

    _columns = {
        'name': fields.char('Nombre archivo'),
        'ruta': fields.char('Ruta al archivo'),
        'invoice_id': fields.many2one('account.invoice', 'Factura/Nota', readonly=True),
        'codigo_sii': fields.char('Codigo DTE SII', size=16, readonly=True),
        'folio_dte_sii': fields.char('Folio DTE SII', size=64, readonly=True),
        'estado_dte': fields.char('Estado DTE', size=64, readonly=True),
        'detalle': fields.text('Detalle', readonly=True),
        'track_id': fields.char('Track ID SII', size=64),
        'fecha': fields.date('Fecha', readonly=True),
        'imprimir': fields.boolean('Imprimir'),
    }

    _defaults = {
        'fecha': fields.date.context_today,
        'imprimir': False,
    }

    def rut_sin_dv(self, rut):
        rut = rut.replace('-','',1).replace('.','',2)
        rut = rut[:-1]
        return rut

    def descargar_xml(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe descargar un XML a la vez.'
        res = dict()
        dte = self.browse(cr, uid, ids[0])
        ruta = dte.ruta
        archivo = dte.name
        if ruta and archivo:
            url = '/web/binary/descargar_xml?ruta=' + ruta
            url += '&nombre_archivo=' + archivo
            res['type'] = 'ir.actions.act_url'
            res['url'] = url
            res['target'] = 'self'
        return res

    def consultar_estado(self, cr, uid, ids, mc_dte_config_id, context=None):
        hash_dte = mc_dte_config_id.hash_tienda
        servidor = mc_dte_config_id.servidor_dte
        rut_emisor = self.rut_sin_dv(mc_dte_config_id.rutemisor)
        Cliente = LibreDTE(hash_dte, servidor)
        detalle = ''
        for dte in self.browse(cr, uid, ids, context=context):
            folio = dte.folio_dte_sii
            dte_cod = dte.codigo_sii
            estado = Cliente.get('/dte/dte_emitidos/estado/'+str(dte_cod)+'/'+str(folio)+'/'+str(rut_emisor))
            if type(estado.json()) == type(dict()):
                detalle = estado.json()['ESTADO'] + ' // '
                if 'GLOSA_ESTADO' in estado.json():
                    detalle += estado.json()['GLOSA_ESTADO'] + ' // '
                else:
                    detalle += 'SIN GLOSA ESTADO // '
                if 'GLOSA_ERR' in estado.json():
                    detalle += estado.json()['GLOSA_ERR'] + ' // '
                else:
                    detalle += 'SIN GLOSA ERROR // '
                if 'NUM_ATENCION' in estado.json():
                    detalle += estado.json()['NUM_ATENCION'] + ' // '
                else:
                    detalle += 'SIN NUM ATENCION // '
                if 'ERR_CODE' in estado.json():
                    detalle += estado.json()['ERR_CODE']
                else:
                    detalle += 'SIN ERR CODE'
            else:
                detalle = estado.json()
            write_vals = {'detalle': detalle}
            self.write(cr, uid, [dte.id], write_vals)
        return detalle

    def actualizar_estado(self, cr, uid, ids, mc_dte_config_id, context=None):
        logger = logging.getLogger('actualizar estado')
        hash_dte = mc_dte_config_id.hash_tienda
        servidor = mc_dte_config_id.servidor_dte
        metodo = mc_dte_config_id.metodo_actualizacion
        rut_emisor = self.rut_sin_dv(mc_dte_config_id.rutemisor)
        Cliente = LibreDTE(hash_dte, servidor)
        estado_txt = ''
        track_id = ''
        for dte in self.browse(cr, uid, ids, context=context):
            folio = dte.folio_dte_sii
            dte_cod = dte.codigo_sii
            estado = Cliente.get('/dte/dte_emitidos/actualizar_estado/'+str(dte_cod)+'/'+str(folio)+'/'+str(rut_emisor)+'?usarWebservice='+str(metodo))
            if type(estado.json()) == type(dict()):
                estado_txt = str(estado.json()['revision_detalle']) + ' / ' + str(estado.json()['revision_estado'])
                track_id = str(estado.json()['track_id'])
                write_vals = {'estado_dte': estado_txt}
                write_vals['track_id'] = track_id
                if 'revision_detalle' in estado.json() and estado.json()['revision_detalle']:
                    if 'ACEPTADO' in estado.json()['revision_detalle'].upper():
                        write_vals['imprimir'] = True
                self.write(cr, uid, [dte.id], write_vals)
            else:
                estado_txt = estado.json()
                track_id = 0
                write_vals = {'estado_dte': estado_txt}
                write_vals['track_id'] = track_id
                self.write(cr, uid, [dte.id], write_vals)
        return estado_txt, track_id

    def consultar_dte(self, cliente, dicc_dte, xml):
        logger = logging.getLogger('consultar dte')
        soup = BeautifulSoup(xml,'xml')
        datos = {
            "emisor": dicc_dte['Encabezado']['Emisor']['RUTEmisor'],
            "dte": dicc_dte['Encabezado']['IdDoc']['TipoDTE'],
            "folio": dicc_dte['Encabezado']['IdDoc']['Folio'],
            "fecha": soup.Encabezado.IdDoc.FchEmis.string,
            "total": soup.Encabezado.Totales.MntTotal.string,
        }
        consultar = cliente.post('/dte/dte_emitidos/consultar?getXML=0', datos)
        if consultar.status_code!=200 :
            error_dte = elimina_tildes(consultar.json())
            logger.warn(error_dte)
            raise osv.except_osv("Error","No fue posible realizar la consulta al DTE.")
            return False
        else:
            return consultar.json()

    def emitir_dte(self, cliente, dicc_dte):
        logger = logging.getLogger('emitir dte')
        emitir = cliente.post('/dte/documentos/emitir', dicc_dte)
        if emitir.status_code!=200 :
            error_dte = elimina_tildes(emitir.json())
            logger.warn(error_dte)
            raise osv.except_osv("Error","No se pudo emitir el DTE.")
            return False
        else:
            return emitir

    def generar_dte(self, cliente, emitir):
        logger = logging.getLogger('generar dte')
        generar = cliente.post('/dte/documentos/generar', emitir.json())
        if generar.status_code!=200 :
            error_dte = elimina_tildes(generar.json())
            logger.warn(error_dte)
            raise osv.except_osv("Error","No fue posible generar el DTE.")
            return False, False, False
        else:
            dte = str(generar.json()['dte'])
            folio = str(generar.json()['folio'])
            emitir_dicc = emitir.json()
            emisor = str(emitir_dicc['emisor'])
            return dte, folio, emisor

    def xml_dte(self, cliente, dte, folio, emisor):
        logger = logging.getLogger('xml dte')
        obtener_xml = cliente.get('/dte/dte_emitidos/xml/'+dte+'/'+folio+'/'+emisor)
        if obtener_xml.status_code!=200:
            error_dte = elimina_tildes(obtener_xml.json())
            logger.warn(error_dte)
            raise osv.except_osv("Error","No se pudo obtener el archivo XML.")
            return False
        else:
            xml = base64.b64decode(obtener_xml.json())
            return xml

    def ted_dte(self, cliente, dte, folio, emisor):
        logger = logging.getLogger('ted dte')
        obtener_ted = cliente.get('/dte/dte_emitidos/ted/'+dte+'/'+folio+'/'+emisor)
        if obtener_ted.status_code!=200 :
            error_dte = elimina_tildes(obtener_ted.json())
            logger.warn(error_dte)
            raise osv.except_osv("Error","No se pudo obtener el archivo PNG.")
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
        logger = logging.getLogger('chequear_existencia')
        emisor = dicc_dte['Encabezado']['Emisor']['RUTEmisor']
        folio = dicc_dte['Encabezado']['IdDoc']['Folio']
        dte = dicc_dte['Encabezado']['IdDoc']['TipoDTE']

        # se obtiene primero el xml del servidor para ver si existe.
        obtener_xml = cliente_ws.get('/dte/dte_emitidos/xml/'+str(dte)+'/'+str(folio)+'/'+str(emisor))
        if obtener_xml.status_code != 200:
            return False, 'No existe', dict()
        else:
            xml = base64.b64decode(obtener_xml.json())
            soup = BeautifulSoup(xml,'xml')
            cliente_dte = soup.Encabezado.Receptor.RUTRecep.string
            fecha = soup.Encabezado.IdDoc.FchEmis.string
            monto_total = soup.Encabezado.Totales.MntTotal.string
            
            dicc_res = dict()
            dicc_res['emisor'] = emisor
            dicc_res['dte'] = dte
            dicc_res['folio'] = folio
            dicc_res['cliente_dte'] = cliente_dte
            dicc_res['fecha_dte'] = fecha
            dicc_res['monto_total'] = monto_total
            return True, 'Existe', dicc_res

    def quitar_folio(self, dicc_dte):
        del dicc_dte['Encabezado']['IdDoc']['Folio']
        folio = dicc_dte['Encabezado']['IdDoc'].get('Folio', False)
        if folio:
            raise osv.except_osv("Error","No se pudo eliminar la clave Folio")
            return False
        return dicc_dte

    def dte_sii(self, cr, uid, dicc_dte={}, dicc_usuario={},context=None):
        logger = logging.getLogger('dte sii')
        # el dicc_dte es un diccionario de python que debe cumplir con las
        # especificaciones de https://github.com/LibreDTE/libredte-lib/tree/master/examples/json
        # hay un ejemplo contenido en este modulo en examples/ejemplo.json
        
        # dicc_usuario es un diccionario que debe contener lo siguiente:
        # servidor de LibreDTE
        # hash de usuario en el servidor de LibreDTE
        # tipo_dte esta clave se usa para identificar el objeto del cual
        # proviene y determinara su tipo (picking, invoice, pos order)
        # ruta_archivos, pruebas y otra informacion que este establecida
        # en el objeto mc.dte.config
        mc_dte_id = False
        if dicc_dte and dicc_usuario:

            servidor = dicc_usuario['servidor']
            hash_dte = dicc_usuario['hash_dte']
            tipo_dte = dicc_usuario['tipo_dte'] #picking_id, invoice_id, posorder_id // Nombre del campo
            id_externo = int(dicc_usuario['id_externo']) #picking_id, invoice_id, posorder_id // ID objeto externo
            ruta_archivos = dicc_usuario['ruta_archivos'] or False
            pruebas = dicc_usuario['dte_pruebas']
            enviar_num_folio = dicc_usuario['enviar_num_folio']
            dte_permitidos = dicc_usuario['dte_permitidos']
            dte_act = dicc_dte['Encabezado']['IdDoc']['TipoDTE']
            
            if not dte_permitidos or dte_act not in dte_permitidos:
                raise osv.except_osv("Error","No puede generar este tipo de documento.")
                return False

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
                error_dte += 'Fecha: '+str(fecha_dte)+'\n'
                raise osv.except_osv( 'Error!',
                "El DTE ya existe con los siguientes datos. Error: %s"%error_dte)
                return False

                #if pruebas:
                #    return True
            else:
                # crear DTE temporal
                emitir = self.emitir_dte(Cliente, dicc_dte)
                logger.warn(emitir.json())

                # se ejecuta hasta aca si esta en modo de pruebas
                if pruebas:
                    return 0

                # crear DTE real
                dte, folio, emisor = self.generar_dte(Cliente, emitir)

            # crear un mc.dte con los datos obtenidos, pero primero 
            # buscar para ver si ya existe
            filtro = [(tipo_dte,'=',id_externo)]
            mc_dte_ids = self.search(cr, uid, filtro)

            if not mc_dte_ids:
                logger.warn('if not mc_dte_ids')
                create_vals = dict()
                create_vals[tipo_dte] = id_externo
                create_vals['estado_dte'] = 'Borrador'
                md_id = self.create(cr, uid, create_vals)
                mc_dte_ids += [md_id]

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

            if mc_dte_ids and len(mc_dte_ids) == 1:
                logger.warn('if mc_dte_ids and len(mc_dte_ids) == 1')
                consulta = self.consultar_dte(Cliente, dicc_dte, xml)
                # escribir / actualizar
                write_vals = dict()
                write_vals['name'] = nombre_archivo
                write_vals['ruta'] = ruta_archivos
                write_vals['codigo_sii'] = dte
                write_vals['folio_dte_sii'] = folio
                write_vals['estado_dte'] = consulta['revision_estado']
                write_vals['track_id'] = consulta['track_id']
                self.write(cr, uid, mc_dte_ids, write_vals)
                mc_dte_id = mc_dte_ids[0]
            else:
                raise osv.except_osv("Error","Hay mas de un registro (mc.dte) para este DTE.")
                return False
        # devuelve el id del mc.dte creado.
        return mc_dte_id

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

class mc_dte_config(osv.osv):
    """Este objeto se usara para establecer algunos parametros de
    configuracion que deben ser utilizados en los DTE.
    """

    texto_folio = """Al seleccionar esta opcion se enviara el numero de folio por este sistema, de lo contrario se usara el entregado por LibreDTE."""

    texto_ruta = """Esta es la ruta en su servidor que usara para guardar los archivos XML y PNG. Debe terminar en una barra inclinada (/)."""

    texto_pruebas = """Seleccione esta opcion si solo esta realizando pruebas y aun no genera DTE reales."""
    
    texto_metodo = """Ingrese el valor 1 para actualizar via servicio web o 0 para actualizar via correo (mas lento)."""

    _name = 'mc.dte.config'

    _columns = {
        'name': fields.char('Nombre'),
        'servidor_dte': fields.char('Servidor DTE'),
        'sucursal_sii': fields.char('Código de sucursal SII'),
        'ruta_archivos': fields.char('Ruta archivos (?)', help=texto_ruta),
        'dte_permitidos': fields.many2many('mc.tipo.dte', 'dte_permitido_rel', 'mc_dte_config_id', 'dte_id', 'DTE permitidos'),
        'hash_tienda': fields.char('Hash Tienda'),
        'dte_pruebas': fields.boolean('Pruebas (?)',help=texto_pruebas),
        'enviar_num_folio': fields.boolean('Enviar numero de folio (?)',help=texto_folio),
        'rutemisor': fields.char('RUT', size=18),
        'razonsocial': fields.char('Razon Social'),
        'giroemisor': fields.char('Giro'),
        'acteco': fields.char('ACTECO'),
        'direccionorigen': fields.char('Direccion'),
        'comunaorigen': fields.char('Comuna'),
        'ciudadorigen': fields.char('Ciudad'),
        'metodo_actualizacion': fields.char('Metodo de actualizacion (?)', help=texto_metodo),
        'direccionessucursales': fields.text('Sucursales'),
        'direccioncasamatriz': fields.text('Casa Matriz'),
        'oficinasii': fields.char('Oficina SII'),
        'infocontacto': fields.char('Contacto'),
    }

mc_dte_config()

class mc_referencia_dte(osv.osv):
    _name = 'mc.referencia.dte'


    # se debe agregar una constraint que obligue a seleccionar un tipo de movimiento
    # si el documento referenciado es DTE
    lista_cod_ref = [
        ('1','Anula documento'),
        ('2','Corrige texto'),
        ('3','Corrige montos'),
    ]

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Factura/Nota', ondelete='cascade', select=True),
        'fecha': fields.date('Fecha referencia', required=True),
        'tipo_doc_ref_id': fields.many2one('mc.referencia.dte.docs','Documento referenciado', required=True),
        'folio_doc_ref': fields.char('Folio o N° doc. ref.', size=24, required=True),
        'cod_ref': fields.selection(lista_cod_ref,'Codigo ref.'),
        'razon_ref': fields.char('Razon referencia', size=100),
        'ref_global': fields.boolean('Global'),
    }

    def _revisar_tipo_doc(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.invoice_id:
                cod_sii = record.invoice_id.journal_id.sii_dte
                if not cod_sii:
                    return True
                if cod_sii not in ['61','56']:
                    return True
                if record.tipo_doc_ref_id:
                    mtd = self.pool.get('mc.tipo.dte')
                    dte_ids = mtd.search(cr, uid, [])
                    lista_dte = [m.codigo_sii for m in mtd.browse(cr, uid, dte_ids)]
                    if record.tipo_doc_ref_id.codigo in lista_dte and not record.cod_ref:
                        return False
                    if record.tipo_doc_ref_id.codigo in lista_dte and not record.razon_ref:
                        return False
        return True

    _constraints = [(_revisar_tipo_doc, 'Debe agregar un codigo y una razon de referencia (Codigo ref., Razon referencia).', ['tipo_doc_ref_id'])]

mc_referencia_dte()

class mc_referencia_dte_docs(osv.osv):
    _name = 'mc.referencia.dte.docs'

    _columns = {
        'name': fields.char('Documento', size=24, required=True),
        'codigo': fields.char('Codigo', size=8, required=True),
    }

mc_referencia_dte_docs()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'referencia_ids': fields.one2many('mc.referencia.dte', 'invoice_id', 'Referencias', readonly=True, states={'draft':[('readonly',False)]}),
        'mc_dte_id': fields.many2one('mc.dte', 'Registro DTE', readonly=True),
    }

    def imprime_dte(self, cr, uid, inv, context=None):
        self.write(cr, uid, [inv.id], {'sent': True}, context=context)
        datas = {
             'ids': [inv.id],
             'model': 'account.invoice',
             'form': self.read(cr, uid, inv.id, context=context)
        }
        if inv.journal_id.reporte_dte_id:
            report_name = inv.journal_id.reporte_dte_id.report_name
        else:
            report_name = 'factura.nota.webkit'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            'nodestroy' : True
        }

    def invoice_print(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe imprimir un documento a la vez.'
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.mc_dte_id:
            if inv.mc_dte_id.imprimir:
                res = self.imprime_dte(cr, uid, inv, context=context)
            else:
                raise osv.except_osv("Error","Primero debe actualizar el estado del DTE y este no debe ser Rechazado.")
                return False
        else:
            res = super(account_invoice, self).invoice_print(cr, uid, ids, context=context)
        return res

    def consultar_estado_dte(self, cr, uid, ids, context=None):
        dte_obj = self.pool.get('mc.dte')
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.mc_dte_id:
                mc_dte_config_id = inv.journal_id.mc_dte_config_id
                detalle = dte_obj.consultar_estado(cr, uid, [inv.mc_dte_id.id], mc_dte_config_id, context=context)
                mensaje = detalle
                self.message_post(cr, uid, [inv.id], body=tools.ustr(mensaje), context=context)
        return True

    def actualizar_estado_dte(self, cr, uid, ids, context=None):
        dte_obj = self.pool.get('mc.dte')
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.mc_dte_id:
                mc_dte_config_id = inv.journal_id.mc_dte_config_id
                estado, track_id = dte_obj.actualizar_estado(cr, uid, [inv.mc_dte_id.id], mc_dte_config_id, context=context)
                mensaje = '<b>DTE actualizado:</b><br>'
                mensaje += 'Revision: ' + str(estado) + '<br>'
                mensaje += 'Track ID: ' + str(track_id) + '<br>'
                self.message_post(cr, uid, [inv.id], body=tools.ustr(mensaje), context=context)
        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        self.dte_invoice(cr, uid, ids, context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.mc_dte_id:
                if inv.mc_dte_id.estado_dte != 'Borrador':
                    raise osv.except_osv("Error","El documento tiene un DTE asociado y no se puede cancelar.")
                    return False
        return res

    def generar_dicc_usuario(self, cr, uid, inv, context=None):
        res = collections.OrderedDict()
        res['servidor'] = inv.journal_id.mc_dte_config_id.servidor_dte
        res['sucursal_sii'] = inv.journal_id.mc_dte_config_id.sucursal_sii
        res['ruta_archivos'] = inv.journal_id.mc_dte_config_id.ruta_archivos
        res['dte_permitidos'] = [dpe.codigo_sii for dpe in inv.journal_id.mc_dte_config_id.dte_permitidos]
        res['hash_dte'] = inv.journal_id.mc_dte_config_id.hash_tienda
        res['dte_pruebas'] = inv.journal_id.mc_dte_config_id.dte_pruebas
        res['enviar_num_folio'] = inv.journal_id.mc_dte_config_id.enviar_num_folio
        res['tipo_dte'] = 'invoice_id'
        res['id_externo'] = inv.id
        return res

    def generar_dicc_dte(self, cr, uid, inv, context=None):
        res = collections.OrderedDict()
        res['Encabezado'] = collections.OrderedDict()
        res['Encabezado']['IdDoc'] = collections.OrderedDict()
        res['Encabezado']['Emisor'] = collections.OrderedDict()
        res['Encabezado']['Receptor'] = collections.OrderedDict()
        res['Encabezado']['IdDoc']['TipoDTE'] = inv.journal_id.sii_dte
        res['Encabezado']['IdDoc']['Folio'] = inv.number
        res['Encabezado']['Emisor']['RUTEmisor'] = inv.journal_id.mc_dte_config_id.rutemisor
        res['Encabezado']['Emisor']['RznSoc'] = inv.journal_id.mc_dte_config_id.razonsocial
        res['Encabezado']['Emisor']['GiroEmis'] = inv.journal_id.mc_dte_config_id.giroemisor
        res['Encabezado']['Emisor']['Acteco'] = inv.journal_id.mc_dte_config_id.acteco
        res['Encabezado']['Emisor']['DirOrigen'] = inv.journal_id.mc_dte_config_id.direccionorigen
        res['Encabezado']['Emisor']['CmnaOrigen'] = inv.journal_id.mc_dte_config_id.comunaorigen
        res['Encabezado']['Emisor']['CiudadOrigen'] = inv.journal_id.mc_dte_config_id.ciudadorigen
        res['Encabezado']['Receptor']['RUTRecep'] = inv.partner_id.rut_cliente
        res['Encabezado']['Receptor']['RznSocRecep'] = inv.partner_id.name
        res['Encabezado']['Receptor']['GiroRecep'] = inv.partner_id.giro_cliente
        res['Encabezado']['Receptor']['DirRecep'] = inv.partner_id.street 
        res['Encabezado']['Receptor']['CmnaRecep'] = inv.partner_id.state_id.name
        res['Detalle'] = list()
        descuento_global = True
        porcentaje_desc_global = 0.0
        for linea in inv.invoice_line:
            linea_dicc = collections.OrderedDict()
            if linea.product_id.default_code:
                linea_dicc['CdgItem'] = collections.OrderedDict()
                linea_dicc['CdgItem']['TpoCodigo'] = 'INT1'
                linea_dicc['CdgItem']['VlrCodigo'] = linea.product_id.default_code
            linea_dicc['NmbItem'] = linea.name
            linea_dicc['QtyItem'] = linea.quantity
            linea_dicc['PrcItem'] = linea.price_unit

            if linea.discount:
                # para que sea descuento global todos los porcentajes
                # deben ser los mismos, de lo contrario se aplica
                # descuento por linea y no global
                if porcentaje_desc_global:
                    if linea.discount != porcentaje_desc_global:
                        descuento_global = False
                # si hay solo una linea y esa linea tiene porcentaje de
                # descuento se aplica global
                porcentaje_desc_global = linea.discount
                linea_dicc['DescuentoPct'] = linea.discount
            else:
                descuento_global = False

            res['Detalle'] += [linea_dicc]

        if not res['Detalle']:
            raise osv.except_osv("Error","El documento no contiene lineas.")
            return False
        
        if descuento_global and porcentaje_desc_global > 0.0:
            # quitar los descuentos por linea para no duplicar los descuentos
            # y agregar los valores de descuento global al diccionario
            for linea_det in res['Detalle']:
                if 'DescuentoPct' in linea_det:
                    # quitar clave y valor
                    del linea_det['DescuentoPct']
            res['DscRcgGlobal'] = list()
            desc_dicc = collections.OrderedDict()
            desc_dicc['NroLinDR'] = 1
            desc_dicc['TpoMov'] = 'D'
            desc_dicc['TpoValor'] = '%'
            desc_dicc['ValorDR'] = porcentaje_desc_global
            res['DscRcgGlobal'] += [desc_dicc]

        res['Referencia'] = list()
        r = 1
        for ref in inv.referencia_ids:
            ref_dicc = collections.OrderedDict()
            ref_dicc['NroLinRef'] = r
            ref_dicc['TpoDocRef'] = ref.tipo_doc_ref_id.codigo
            if ref.ref_global:
                ref_dicc['IndGlobal'] = 'true'
                ref_dicc['FolioRef'] = '0'
            else:
                ref_dicc['FolioRef'] = ref.folio_doc_ref
            ref_dicc['FchRef'] = ref.fecha
            ref_dicc['CodRef'] = ref.cod_ref
            ref_dicc['RazonRef'] = ref.razon_ref
            res['Referencia'] += [ref_dicc]
            r += r
        return res

    def dte_invoice(self, cr, uid, ids, context=None):
        dte_obj = self.pool.get('mc.dte')
        for inv in self.browse(cr, uid, ids, context=context):
            # se debe comprobar que el DTE este autorizado para esta sucursal
            # el tipo de DTE (codigo SII) se debe almacenar en el diario
            # y esa informacion verificar que este en dicc_u['dte_permitidos']
            if inv.journal_id.mc_dte_config_id and inv.journal_id.sii_dte:
                if inv.journal_id.sii_dte in ['60','61']:
                    if not inv.referencia_ids:
                        raise osv.except_osv('Error', u'Debe agregar por lo menos una referencia.')
                        return False
                dicc_u = self.generar_dicc_usuario(cr, uid, inv, context)
                dicc_d = self.generar_dicc_dte(cr, uid, inv, context)
                mc_dte_id = dte_obj.dte_sii(cr, uid, dicc_d, dicc_u, context)
                if mc_dte_id != 0:
                    self.write(cr, uid, [inv.id], {'mc_dte_id':mc_dte_id})
                    mc_dte = dte_obj.browse(cr, uid, mc_dte_id)
                    mensaje = '<b>DTE creado:</b><br>'
                    mensaje += 'Tipo: ' + str(mc_dte.codigo_sii) + '<br>'
                    mensaje += 'Folio: ' + str(mc_dte.folio_dte_sii) + '<br>'
                    mensaje += 'Track ID: ' + str(mc_dte.track_id) + '<br>'
                    self.message_post(cr, uid, [inv.id], body=tools.ustr(mensaje), context=context)
                    dte_obj.write(cr, uid, [mc_dte_id], {'invoice_id': inv.id})
        return True

account_invoice()
