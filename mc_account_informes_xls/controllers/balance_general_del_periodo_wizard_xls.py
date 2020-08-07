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

import time, re, pprint, pytz
import xlwt

from datetime import datetime
from cStringIO import StringIO

from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

class mc_archivo_xls_bgp(osv.osv):
    _name = 'mc.archivo.xls.bgp'

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

    def reporte_resumen(self, cr, uid, libro, data_dicc):
        l = data_dicc[0]
        estilo1 = xlwt.easyxf('font: bold 1')
        estilo2 = xlwt.easyxf(num_format_str='@')
        hportada = libro.add_sheet('Resumen')
        columnas = ['Agrupacion']
        columnas += ['Saldo deudor']
        columnas += ['Saldo acreedor']
        for c, elemento in enumerate(columnas):
            hportada.write(0, c, elemento, estilo1)
            hportada.col(c).width = 256 * (len(elemento) + 2)
        fila = 1
        
        hportada.write(fila, 0, l['r_nombre_activo'])
        hportada.write(fila, 1, round(l['r_saldo_deudor_activo']))
        hportada.write(fila, 2, round(l['r_saldo_acreedor_activo']))
        fila += 1
        
        hportada.write(fila, 0, l['r_nombre_pasivo'])
        hportada.write(fila, 1, round(l['r_saldo_deudor_pasivo']))
        hportada.write(fila, 2, round(l['r_saldo_acreedor_pasivo']))
        fila += 1
        
        hportada.write(fila, 0, 'Total')
        hportada.write(fila, 1, round(l['r_total_saldo_deudor_activo_pasivo']))
        hportada.write(fila, 2, round(l['r_total_saldo_acreedor_activo_pasivo']))
        fila += 1
        
        hportada.write(fila, 0, 'Resultado')
        hportada.write(fila, 1, round(l['r_resultado_activo_pasivo_deudor']))
        hportada.write(fila, 2, round(l['r_resultado_activo_pasivo_acreedor']))
        fila += 1
        
        fila += 1
        
        hportada.write(fila, 0, l['r_nombre_perdida'])
        hportada.write(fila, 1, round(l['r_saldo_deudor_perdida']))
        hportada.write(fila, 2, round(l['r_saldo_acreedor_perdida']))
        fila += 1
        
        hportada.write(fila, 0, l['r_nombre_ganancia'])
        hportada.write(fila, 1, round(l['r_saldo_deudor_ganancia']))
        hportada.write(fila, 2, round(l['r_saldo_acreedor_ganancia']))
        fila += 1
        
        hportada.write(fila, 0, 'Total')
        hportada.write(fila, 1, round(l['r_total_saldo_deudor_perdida_ganancia']))
        hportada.write(fila, 2, round(l['r_total_saldo_acreedor_perdida_ganancia']))
        fila += 1
        
        hportada.write(fila, 0, 'Resultado')
        hportada.write(fila, 1, round(l['r_resultado_perdida_ganancia_deudor']))
        hportada.write(fila, 2, round(l['r_resultado_perdida_ganancia_acreedor']))
        fila += 1
        return libro

    def reporte_detalle(self, cr, uid, libro, data_dicc):
        return libro

    def reporte_libro(self, cr, uid, libro, data_dicc):
        for ele in data_dicc:
            if ele.has_key('resumen'):
                libro = self.reporte_resumen(cr, uid, libro, ele['resumen'])
            elif ele.has_key('detalle'):
                libro = self.reporte_detalle(cr, uid, libro, ele['detalle'])
        return libro

    def libro_xls_bgp(self, cr, uid, data_dicc):
        libro = xlwt.Workbook()
        libro = self.reporte_libro(cr, uid, libro, data_dicc)
        return libro

    def archivo_libro(self, cr, uid, data_dicc):
        libro = self.libro_xls_bgp(cr, uid, data_dicc)
        fp = StringIO()
        libro.save(fp)
        fp.seek(0)
        archivo = fp.read()
        fp.close()
        return archivo
