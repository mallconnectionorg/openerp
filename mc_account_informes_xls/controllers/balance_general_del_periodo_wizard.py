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
from datetime import datetime
from report import report_sxw

from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

class balance_general_del_periodo_wizard(osv.osv):
    
    _name = 'balance.general.del.periodo.wizard'

    def get_cabecera(self, cr, uid, data=False):
        result = []
        if not data:
            return result
        periodo = data['periodo_id']
        compania_id = data['compania_id']
        cr = self.cursor
        sql = "SELECT rc.name, rc.logo_web as logo FROM res_company rc WHERE id=%d"
        cr.execute(sql % (compania_id))
        recordset = self.cr.dictfetchall()

        if (len(recordset)>=1):
            for row in recordset:
                result.append({
                    'periodo': periodo,
                    'logo': row['logo'],
                    'nombres': row['name'],
                })
        return result

    def get_detalle(self, cr, uid, form):
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')

        plan_cuentas = account_obj.search(cr, uid, [('parent_id', '=', False)])
        plan_cuentas_obj = account_obj.browse(cr, uid, plan_cuentas)
        
        parent_left = {}
        result_balance_totales_y_resumen = []
        
        for plan_cuenta in plan_cuentas_obj:
            if not parent_left:
                account_ids = account_obj.search(cr, uid, [('company_id', '=',plan_cuenta.company_id.id)])
                account_obj = account_obj.browse(cr, SUPERUSER_ID, account_ids)
                for aux in account_obj:
                    parent_left[aux.code] = aux.parent_left
            
            periodo = period_obj.browse(cr, uid, int(form['periodo_id']))
            
            mes_contable = periodo.id
            ano_contable = periodo.fiscalyear_id.id
            plan_cuenta = plan_cuenta.id
            
            nivel = form['nivel']
            mostrar_cuentas = form['mostrar_cuentas']
            
            sql_balance_periodo = """
            WITH RECURSIVE x AS (

                SELECT account_account.id,account_account.code,account_account.name
                FROM res_company
                INNER JOIN account_account ON account_account.company_id = res_company.id 
                --NECESARIO PARA BUSCAR EL TIPO DE CUENTA (REPORT_TYPE)
                INNER JOIN account_account_type ON account_account_type.id = account_account.user_type
                WHERE account_account.id = '%s'

                UNION ALL

                SELECT account_account.id,account_account.code,account_account.name
                FROM x
                JOIN account_account ON (account_account.id = x.id)
                INNER JOIN res_company ON account_account.company_id = res_company.id 
            )
            SELECT id,code,name,level,type,parent_left,
            (
                SELECT
                "account_account_type"."report_type"
                FROM
                "account_account_type"
                where
                "account_account_type"."id" = "user_type"
            ) AS "typo_reporte",
            (
            SELECT 
            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance_inicial
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND special)  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance_inicial,

            (
            SELECT 
            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance_anterior
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND NOT special AND id < '%s')  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance_anterior,

            (
            SELECT 
            COALESCE(SUM(l.debit), 0) as debit 
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s')  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as debit,
            (
            SELECT 
            COALESCE(SUM(l.credit), 0) as credit
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s')  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as credit,
            (
            SELECT 
            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s')  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance,
            (
            SELECT name FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s'
            ) as nombre_periodo
            FROM account_account principal
            where principal.level >= 1 and principal.level <= '%s'
            order by parent_left
            """
            
            # Obtención de Datos - Balance
            cr.execute(sql_balance_periodo % (plan_cuenta, ano_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable,nivel))
            recordset_balance_periodo = cr.dictfetchall()
            
            # Obtención de Datos - Nivel 6 - para que las sumas no cambien cuando se cambia de nivel
            cr.execute(sql_balance_periodo % (plan_cuenta, ano_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable,6))
            recordset_balance_nivel_6 = cr.dictfetchall()
            
            result_balance_periodo = []
            result_resumen = []

            saldo_inicial = 0
            calcular_saldo = 0
            deudores = 0
            acreedores = 0
            
        # ----------para el resumen-------------
            #activo
            r_nombre_activo = ''
            r_saldo_deudor_activo = r_saldo_acreedor_activo = 0     
            #pasivo
            r_nombre_pasivo = ''
            r_saldo_deudor_pasivo = r_saldo_acreedor_pasivo = 0     
            #perdida
            r_nombre_perdida = ''
            r_saldo_deudor_perdida = r_saldo_acreedor_perdida = 0
            #ganancia
            r_nombre_ganancia = ''
            r_saldo_deudor_ganancia = r_saldo_acreedor_ganancia = 0
            
            r_total_saldo_deudor_activo_pasivo = r_total_saldo_acreedor_activo_pasivo = 0
            r_resultado_activo_pasivo_deudor = r_resultado_activo_pasivo_acreedor = 0
            r_total_saldo_deudor_perdida_ganancia = r_total_saldo_acreedor_perdida_ganancia = 0     
            r_resultado_perdida_ganancia_deudor = r_resultado_perdida_ganancia_acreedor = 0     

            for campo in recordset_balance_nivel_6:
                saldo_inicial = float(campo['balance_inicial']) + float(campo['balance_anterior'])
                        

                debit=float(campo['debit'])
                credit=float(campo['credit'])   
                if saldo_inicial < 0:
                    debit = debit + (saldo_inicial * -1)
                else:
                    credit = credit + saldo_inicial
                    
                calcular_saldo = debit - credit
                
                if calcular_saldo < 0:
                    deudores = abs(calcular_saldo)
                else:
                    acreedores = abs(calcular_saldo)


                if campo['code'] == '1':
                    r_nombre_activo = campo['name']
                if campo['code'] in ['2']:
                    r_nombre_pasivo = campo['name']
                if campo['code'] in ['5']:
                    r_nombre_perdida = campo['name']
                if campo['code'] in ['4']:
                    r_nombre_ganancia = campo['name']

                if campo['type'] and campo['type'] != 'view':
                    if campo['code'][:1] == '1':
                        r_saldo_deudor_activo += float(deudores)
                        r_saldo_acreedor_activo += float(acreedores)                    
                    elif campo['code'][:1] in ['2','3']:
                        r_saldo_deudor_pasivo += float(deudores)
                        r_saldo_acreedor_pasivo += float(acreedores)                    
                    elif campo['code'][:1] in ['5','6']:
                        r_saldo_deudor_perdida += float(deudores)
                        r_saldo_acreedor_perdida += float(acreedores)                   
                    elif campo['code'][:1] in ['4','7']:
                        r_saldo_deudor_ganancia += float(deudores)
                        r_saldo_acreedor_ganancia += float(acreedores)  

                acreedores = 0
                deudores = 0

            if r_saldo_deudor_activo - r_saldo_acreedor_activo > 0:
                r_saldo_deudor_activo = r_saldo_deudor_activo - r_saldo_acreedor_activo
                r_saldo_acreedor_activo = 0
            else:
                r_saldo_acreedor_activo = (r_saldo_deudor_activo - r_saldo_acreedor_activo) * -1 
                r_saldo_deudor_activo = 0

            if r_saldo_deudor_pasivo - r_saldo_acreedor_pasivo > 0:
                r_saldo_deudor_pasivo = r_saldo_deudor_pasivo - r_saldo_acreedor_pasivo
                r_saldo_acreedor_pasivo = 0
            else:
                r_saldo_acreedor_pasivo = (r_saldo_deudor_pasivo - r_saldo_acreedor_pasivo) * -1 
                r_saldo_deudor_pasivo = 0

            if r_saldo_deudor_perdida - r_saldo_acreedor_perdida > 0:
                r_saldo_deudor_perdida = r_saldo_deudor_perdida - r_saldo_acreedor_perdida
                r_saldo_acreedor_perdida = 0
            else:
                r_saldo_acreedor_perdida = (r_saldo_deudor_perdida - r_saldo_acreedor_perdida) * -1 
                r_saldo_deudor_perdida = 0

            if r_saldo_deudor_ganancia - r_saldo_acreedor_ganancia > 0:
                r_saldo_deudor_ganancia = r_saldo_deudor_ganancia - r_saldo_acreedor_ganancia
                r_saldo_acreedor_ganancia = 0
            else:
                r_saldo_acreedor_ganancia = (r_saldo_deudor_ganancia - r_saldo_acreedor_ganancia) * -1 
                r_saldo_deudor_ganancia = 0
            
            for campo in recordset_balance_periodo:
                if mostrar_cuentas == '2':
                    if campo['debit'] or campo['credit'] or (float(campo['balance_inicial']) + float(campo['balance_anterior'])):
                
                        saldo_inicial = float(campo['balance_inicial']) + float(campo['balance_anterior'])
                        
                        debit=float(campo['debit'])
                        credit=float(campo['credit'])   
                        calcular_saldo = saldo_inicial + debit - credit 
                        
                        if calcular_saldo < 0:
                            acreedores = abs(calcular_saldo)
                        else:
                            deudores = abs(calcular_saldo)

                        result_balance_periodo.append({
                            'parent_left': parent_left[campo['code']],
                            'type': (campo['type']) if campo.has_key('type') else '-',
                            'level': (campo['level']) if campo.has_key('level') else '0',
                            'code': (campo['code']) if campo.has_key('code') else '-',
                            'name': (campo['name']) if campo.has_key('name') else '-',
                            'saldo_inicial': saldo_inicial if saldo_inicial else 0,
                            'debit': debit,
                            'credit': credit,
                            'deudores': deudores if deudores else 0,
                            'acreedores': acreedores if acreedores else 0,              
                            })
                else:
                
                        saldo_inicial = float(campo['balance_inicial']) + float(campo['balance_anterior'])
                        
                        debit=float(campo['debit'])
                        credit=float(campo['credit'])   
                        calcular_saldo = saldo_inicial + debit - credit
                        
                        if calcular_saldo < 0:
                            deudores = abs(calcular_saldo)
                        else:
                            acreedores = abs(calcular_saldo)

                        result_balance_periodo.append({
                            'parent_left': parent_left[campo['code']],
                            'type': (campo['type']) if campo.has_key('type') else '-',
                            'level': (campo['level']) if campo.has_key('level') else '0',
                            'code': (campo['code']) if campo.has_key('code') else '-',
                            'name': (campo['name']) if campo.has_key('name') else '-',
                            'saldo_inicial': saldo_inicial if saldo_inicial else 0,
                            'debit': debit,
                            'credit': debit,
                            'deudores': deudores if deudores else 0,
                            'acreedores': acreedores if acreedores else 0,              
                            })
                    
                acreedores = 0
                deudores = 0
            
            r_total_saldo_deudor_activo_pasivo = float(r_saldo_deudor_activo) + float(r_saldo_deudor_pasivo)
            r_total_saldo_acreedor_activo_pasivo = float(r_saldo_acreedor_activo) + float(r_saldo_acreedor_pasivo)      
            r_resultado = float(r_total_saldo_deudor_activo_pasivo) - float(r_total_saldo_acreedor_activo_pasivo)
            
            if r_resultado < 0:
                r_resultado_activo_pasivo_deudor = r_resultado
            else:
                r_resultado_activo_pasivo_acreedor = r_resultado
            
            r_total_saldo_deudor_perdida_ganancia = float(r_saldo_deudor_perdida) + float(r_saldo_deudor_ganancia)
            r_total_saldo_acreedor_perdida_ganancia = float(r_saldo_acreedor_perdida) + float(r_saldo_acreedor_ganancia)        
            r_resultado = float(r_total_saldo_deudor_perdida_ganancia) - float(r_total_saldo_acreedor_perdida_ganancia)
            
            if r_resultado < 0:
                r_resultado_perdida_ganancia_deudor = r_resultado
            else:
                r_resultado_perdida_ganancia_acreedor = r_resultado

            result_resumen.append({
                'r_nombre_activo': r_nombre_activo if r_nombre_activo else '-',
                'r_nombre_pasivo': r_nombre_pasivo if r_nombre_pasivo else '-',
                'r_nombre_perdida': r_nombre_perdida if r_nombre_perdida else '-',
                'r_nombre_ganancia': r_nombre_ganancia if r_nombre_ganancia else '-',
                'r_saldo_deudor_activo': r_saldo_deudor_activo if r_saldo_deudor_activo else 0,
                'r_saldo_acreedor_activo': r_saldo_acreedor_activo if r_saldo_acreedor_activo else 0,
                'r_saldo_deudor_pasivo': r_saldo_deudor_pasivo if r_saldo_deudor_pasivo else 0,
                'r_saldo_acreedor_pasivo': r_saldo_acreedor_pasivo if r_saldo_acreedor_pasivo else 0,
                'r_saldo_deudor_perdida': r_saldo_deudor_perdida if r_saldo_deudor_perdida else 0,
                'r_saldo_acreedor_perdida': r_saldo_acreedor_perdida if r_saldo_acreedor_perdida else 0,
                'r_saldo_deudor_ganancia': r_saldo_deudor_ganancia if r_saldo_deudor_ganancia else 0,
                'r_saldo_acreedor_ganancia': r_saldo_acreedor_ganancia if r_saldo_acreedor_ganancia else 0,
                'r_total_saldo_deudor_activo_pasivo': r_total_saldo_deudor_activo_pasivo if r_total_saldo_deudor_activo_pasivo else 0,
                'r_total_saldo_acreedor_activo_pasivo': r_total_saldo_acreedor_activo_pasivo if r_total_saldo_acreedor_activo_pasivo else 0,
                'r_resultado_activo_pasivo_deudor': r_resultado_activo_pasivo_deudor if r_resultado_activo_pasivo_deudor else 0,
                'r_resultado_activo_pasivo_acreedor': r_resultado_activo_pasivo_acreedor if r_resultado_activo_pasivo_acreedor else 0,
                'r_total_saldo_deudor_perdida_ganancia': r_total_saldo_deudor_perdida_ganancia if r_total_saldo_deudor_perdida_ganancia else 0,
                'r_total_saldo_acreedor_perdida_ganancia': r_total_saldo_acreedor_perdida_ganancia if r_total_saldo_acreedor_perdida_ganancia else 0,
                'r_resultado_perdida_ganancia_deudor': r_resultado_perdida_ganancia_deudor if r_resultado_perdida_ganancia_deudor else 0,
                'r_resultado_perdida_ganancia_acreedor': r_resultado_perdida_ganancia_acreedor if r_resultado_perdida_ganancia_acreedor else 0
                })
                
            result_balance_totales_y_resumen.append({
                'detalle': result_balance_periodo,
                'resumen': result_resumen,
                })
        resumen = False
        detalle_code = {}
        for plan in result_balance_totales_y_resumen:

            detalles = plan['detalle']
            for detalle in detalles:
                code = detalle['code']
                
                if code not in detalle_code:
                    detalle_code[code] = detalle
                else:
                    for sumar in ['saldo_inicial', 'debit', 'credit', 'deudores', 'acreedores']:
                        detalle_code[code][sumar] += detalle[sumar]

            aux_detalle = []
            for code in detalle_code:
                aux_detalle.append(detalle_code[code])

            if not resumen:
                resumen = plan['resumen'][0]
            else:
                for campo in plan['resumen'][0]:
                    if campo not in ['r_nombre_activo', 'r_nombre_pasivo', 'r_nombre_perdida', 'r_nombre_ganancia']:
                        resumen[campo] += plan['resumen'][0][campo]

        ret = [{
            'detalle': [{}],
            'resumen': [{}],
        }]
        ret[0]['detalle'] = sorted(aux_detalle, key=lambda var: var['parent_left'])
        ret[0]['resumen'][0] = resumen

        return ret

balance_general_del_periodo_wizard()
