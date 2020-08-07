#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Informes XLS
#   Copyright (C) 2020 Cesar Lopez Aguillon
#   Mall Connection
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
try:
    import json
except ImportError:
    import simplejson as json

from web.controllers.main import ExcelExport
from openerp import pooler
from cStringIO import StringIO
from datetime import datetime

import web.http as openerpweb
import xlwt
#from xlwt import *
import logging
#import datetime

class DescargaInformesXLS(ExcelExport):
    _cp_path = '/web/binary/descargar_informes_xls'

    def fecha_fecha(self, fecha):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
        except:
            return fecha
        return fecha

    def fecha_hora(self, fecha):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        except:
            return fecha
        return fecha


    def crear_reporte_xls(self, data):
        res = ''
        logger = logging.getLogger('account_crear_reporte_xls')
        cr = pooler.get_db(data['dbname']).cursor()
        uid = data['user']
        tipo = data['tipo']
        bd_obj = pooler.get_pool(data['dbname'])
        if tipo == 'cuenta':
            objeto = bd_obj.get('account.account')
            objeto_browse = objeto.browse(cr, uid, int(data['cuenta_id']))
        elif tipo == 'librobalance':
            tipo_libro = data['reporte']
            if tipo_libro == 'balance_general_periodo':
                objeto = bd_obj.get('balance.general.del.periodo.wizard')
                resbgp = objeto.get_detalle(cr, uid, data)
                logger.warn(resbgp)
                objeto2 = bd_obj.get('mc.archivo.xls.bgp')
                res = objeto2.archivo_libro(cr, uid, resbgp)
                
            elif tipo_libro == 'balance_ocho_columnas':
                objeto = bd_obj.get('balance.ocho.columnas.wizard')
                resboc = objeto.get_detalle(cr, uid, data)
                logger.warn(resboc)
            elif tipo_libro == 'libro_diario':
                objeto = bd_obj.get('libro.diario.wizard')
                resld = objeto.get_detalle(cr, uid, data)
                logger.warn(resld)
            elif tipo_libro == 'inventario_balance':
                objeto = bd_obj.get('inventario.y.balance.wizard')
                resiyb = objeto.get_detalle(cr, uid, data)
                logger.warn(resiyb)
            elif tipo_libro == 'libro_mayor':
                objeto = bd_obj.get('libro.mayor.wizard')
                reslm = objeto.get_detalle(cr, uid, data)
                logger.warn(reslm)
            elif tipo_libro == 'libro_retenciones':
                objeto = bd_obj.get('libro.retenciones.wizard')
                reslr = objeto.get_detalle(cr, uid, data)
                logger.warn(reslr)
        else:
            objeto = data['reporte']
            objeto_browse = False
        
        
        cr.commit() 
        cr.close()
        return res

    @openerpweb.httprequest
    def index(self, req, data):
        data = json.loads(data)
        filename = 'informe_' + data['reporte'] + '.xls'
        headers = [
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Disposition', 'attachment; filename="' + filename + '"'),
            ('charset', 'utf-8'),
        ]
        return req.make_response(self.crear_reporte_xls(data), headers, cookies=None)

