#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  temp.py
#  
#  Copyright 2020 Cesar Lopez Aguillon <cesar@thunder>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
        if company_ids.find(',') != -1 and result_mayor_periodo:

            def order_detalle(result_detalles, saldo_inicial):
                newarray = sorted(result_detalles, key=lambda k: k['date'])
                for aux in newarray:
                    aux['saldo'] = aux['debit'] - aux['credit'] + saldo_inicial
                    saldo_inicial = aux['saldo']
                return newarray

            saldo_inicial = 0
            suma_debit = 0
            suma_credit = 0
            detallee = []
            last_code = result_mayor_periodo[0]
            new_result_mayor_periodo = []
            for aux in result_mayor_periodo:
                if last_code['code'] == aux['code']:
                    saldo_inicial += aux['saldo_inicial']
                    suma_debit += aux['suma_debit']
                    suma_credit += aux['suma_credit']
                    detallee += aux['detallee']
                else:
                    trans = last_code
                    trans['saldo_inicial'] = saldo_inicial
                    trans['suma_debit'] = suma_debit
                    trans['suma_credit'] = suma_credit
                    trans['detallee'] = order_detalle(detallee, saldo_inicial)
                    new_result_mayor_periodo.append(trans)
                    saldo_inicial = aux['saldo_inicial']
                    suma_debit = aux['suma_debit']
                    suma_credit = aux['suma_credit']
                    detallee = aux['detallee']
                last_code = aux
            trans = last_code
            trans['saldo_inicial'] = saldo_inicial
            trans['suma_debit'] = suma_debit
            trans['suma_credit'] = suma_credit
            trans['detallee'] = order_detalle(detallee, saldo_inicial)
            new_result_mayor_periodo.append(trans)
            result_mayor_periodo = new_result_mayor_periodo


{'resumen': 
    [{'r_saldo_deudor_perdida': 0, 
    'r_resultado_perdida_ganancia_acreedor': 62403722.44, 
    'r_nombre_activo': '-', 
    'r_total_saldo_deudor_activo_pasivo': 11856707.3, 
    'r_total_saldo_deudor_perdida_ganancia': 62403722.44, 
    'r_saldo_deudor_activo': 0, 
    'r_resultado_activo_pasivo_deudor': -62403722.44, 
    'r_resultado_perdida_ganancia_deudor': 0, 
    'r_saldo_acreedor_pasivo': 0, 'r_nombre_pasivo': '-', 
    'r_saldo_deudor_ganancia': 62403722.44, 
    'r_saldo_acreedor_perdida': 0, 
    'r_saldo_deudor_pasivo': 11856707.3, 
    'r_saldo_acreedor_ganancia': 0, 
    'r_saldo_acreedor_activo': 74260429.74, 
    'r_nombre_perdida': '-', 
    'r_total_saldo_acreedor_activo_pasivo': 74260429.74, 
    'r_nombre_ganancia': '-', 
    'r_resultado_activo_pasivo_acreedor': 0, 
    'r_total_saldo_acreedor_perdida_ganancia': 0}]

'detalle': 
    [
    {'code': u'100000', 
    'credit': 0.0, 
    'parent_left': 1, 
    'name': u'ACTIVO', 
    'level': 1, 
    'saldo_inicial': 0, 
    'debit': 74260429.74, 
    'type': u'view', 
    'deudores': 74260429.74, 
    'acreedores': 0}, 
    
    {'code': u'110000', 
    'credit': 0.0, 
    'parent_left': 2, 
    'name': u'ACTIVO CIRCULANTE', 
    'level': 2, 
    'saldo_inicial': 0, 
    'debit': 74260429.74, 
    'type': u'view', 
    'deudores': 74260429.74, 
    'acreedores': 0}, 
    
    {'code': u'110400', 
    'credit': 0.0, 
    'parent_left': 37, 
    'name': u'DEUDORES POR VENTA', 
    'level': 3, 
    'saldo_inicial': 0, 
    'debit': 74260429.74, 
    'type': u'view', 
    'deudores': 74260429.74, 
    'acreedores': 0}, 
    
    {'code': u'110401', 
    'credit': 0.0, 
    'parent_left': 38,
    'name': u'CLIENTES', 
    'level': 4, 
    'saldo_inicial': 0, 
    'debit': 74260429.74, 
    'type': u'receivable', 
    'deudores': 74260429.74, 
    'acreedores': 0}, 
    
    {'code': u'200000', 
    'credit': 11856707.3, 
    'parent_left': 151, 
    'name': u'PASIVO', 
    'level': 1, 
    'saldo_inicial': 0, 
    'debit': 0.0, 
    'type': u'view', 
    'deudores': 0, 
    'acreedores': 11856707.3}, 
    
    {'code': u'210000', 
    'credit': 11856707.3, 
    'parent_left': 152, 
    'name': u'PASIVO CIRCULANTE', 
    'level': 2, 
    'saldo_inicial': 0, 'debit': 0.0, 'type': u'view', 'deudores': 0, 'acreedores': 11856707.3}, {'code': u'210400', 'credit': 11856707.3, 'parent_left': 177, 'name': u'IMPUESTOS POR PAGAR', 'level': 3, 'saldo_inicial': 0, 'debit': 0.0, 'type': u'view', 'deudores': 0, 'acreedores': 11856707.3}, {'code': u'210401', 'credit': 11856707.3, 'parent_left': 178, 'name': u'IVA DEBITO FISCAL', 'level': 4, 'saldo_inicial': 0, 'debit': 0.0, 'type': u'other', 'deudores': 0, 'acreedores': 11856707.3}, {'code': u'400000', 'credit': 62403722.44, 'parent_left': 401, 'name': u'GANANCIA', 'level': 1, 'saldo_inicial': 0, 'debit': 0.0, 'type': u'view', 'deudores': 0, 'acreedores': 62403722.44}, {'code': u'410000', 'credit': 62403722.44, 'parent_left': 402, 'name': u'INGRESOS DE EXPLOTACION', 'level': 2, 'saldo_inicial': 0, 'debit': 0.0, 'type': u'view', 'deudores': 0, 'acreedores': 62403722.44}, {'code': u'410100', 'credit': 62403722.44, 'parent_left': 403, 'name': u'VENTAS', 'level': 3, 'saldo_inicial': 0, 'debit': 0.0, 'type': u'view', 'deudores': 0, 'acreedores': 62403722.44}, {'code': u'410101', 'credit': 62403722.44, 'parent_left': 404, 'name': u'VENTAS NACIONALES', 'level': 4, 'saldo_inicial': 0, 'debit': 0.0, 'type': u'other', 'deudores': 0, 'acreedores': 62403722.44}]}
