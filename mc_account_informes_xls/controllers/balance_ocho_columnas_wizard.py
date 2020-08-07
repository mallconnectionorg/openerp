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

class balance_ocho_columnas_wizard(osv.osv):
    
    _name = 'balance.ocho.columnas.wizard'

    def get_cabecera(self, form):
        result = []
        periodo = form['mes_contable'][1]
        compania_id = form['compania'][0]
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
            --NECESARIO PARA BUSCAR EL TIPO DE CUENTA (REPORT_TYPE) /
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
            )AS "typo_reporte",
            (
            SELECT
            COALESCE(SUM(l.debit),0) as balance_inicial_debit
            FROM
            account_move_line l
            WHERE
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND special)  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance_inicial_debit,
            (
            SELECT
            COALESCE(SUM(l.credit), 0) as balance_inicial_credit
            FROM
            account_move_line l
            WHERE
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND special)  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance_inicial_credit,
            (
            SELECT
            COALESCE(SUM(l.debit), 0)as balance_anterior_debit
            FROM
            account_move_line l
            WHERE
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND NOT special AND id < '%s')  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance_anterior_debit,
            (
            SELECT
            COALESCE(SUM(l.credit),0)as balance_anterior_credit
            FROM
            account_move_line l
            WHERE
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND NOT special AND id < '%s')  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as balance_anterior_credit,
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

            cr.execute(sql_balance_periodo % (plan_cuenta, ano_contable,ano_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable,nivel))
            recordset_balance_periodo = cr.dictfetchall()
            
            cr.execute(sql_balance_periodo % (plan_cuenta, ano_contable,ano_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable,6))
            recordset_balance_nivel_6 = cr.dictfetchall()
            
            result_balance_periodo = []
            result_resumen = []

            saldo_inicial = 0
            calcular_saldo = 0
            deudores = 0
            acreedores = 0
            activo = 0
            pasivo = 0
            deficit = 0
            superavit = 0
            
            s_debit = 0
            s_d_debit = 0
            s_i_debit = 0
            s_credit = 0
            s_d_credit = 0
            s_i_credit = 0
            s_deudores = 0
            s_d_deudores = 0
            s_i_deudores = 0
            s_acreedores = 0
            s_d_acreedores = 0
            s_i_acreedores = 0
            s_activo = 0
            s_d_activo = 0
            s_i_activo = 0
            s_pasivo = 0
            s_d_pasivo = 0
            s_i_pasivo = 0
            s_deficit = 0
            s_d_deficit = 0
            s_i_deficit = 0
            s_superavit = 0
            s_d_superavit = 0
            s_i_superavit = 0

            for campo in recordset_balance_nivel_6:
                saldo_inicial_debit = float(campo['balance_inicial_debit']) + float(campo['balance_anterior_debit'])
                saldo_inicial_credit = float(campo['balance_inicial_credit']) + float(campo['balance_anterior_credit'])

                debit=float(campo['debit']) + saldo_inicial_debit
                credit=float(campo['credit']) + saldo_inicial_credit

                calcular_saldo = debit - credit

                if calcular_saldo < 0:
                    deudores = abs(calcular_saldo)
                else:
                    acreedores = abs(calcular_saldo)

                if campo['code'][:1] in ['1','2','3']:
                    if calcular_saldo > 0:
                        activo = abs(calcular_saldo)
                    else:
                        pasivo = abs(calcular_saldo)
                if campo['code'][:1] in ['4','5','6','7']:
                    if calcular_saldo > 0:
                        deficit = abs(calcular_saldo)
                    else:
                        superavit = abs(calcular_saldo)     

                if campo['type'] and campo['type'] != 'view':
                    s_debit += debit                        
                    s_credit += credit
                    s_deudores += float(deudores)
                    s_acreedores += float(acreedores)
                    s_activo += float(activo)
                    s_pasivo += float(pasivo)
                    s_deficit += float(deficit)
                    s_superavit += float(superavit)
                    
                deudores = 0
                acreedores = 0
                activo = 0
                pasivo = 0
                deficit = 0
                superavit = 0
                        
            for campo in recordset_balance_periodo:
                saldo_inicial_debit = float(campo['balance_inicial_debit']) + float(campo['balance_anterior_debit'])
                saldo_inicial_credit = float(campo['balance_inicial_credit']) + float(campo['balance_anterior_credit']) 
                
                debit=float(campo['debit']) + saldo_inicial_debit
                credit=float(campo['credit']) + saldo_inicial_credit    
                    
                calcular_saldo = debit - credit
                
                if calcular_saldo >= 0:
                    deudores = abs(calcular_saldo)
                else:
                    acreedores = abs(calcular_saldo)
                    
                if campo['code'][:1] in ['1','2','3']:
                    if calcular_saldo > 0:
                        activo = abs(calcular_saldo)
                    else:
                        pasivo = abs(calcular_saldo)
                if campo['code'][:1] in ['4','5','6','7']:
                    if calcular_saldo > 0:
                        deficit = abs(calcular_saldo)
                    else:
                        superavit = abs(calcular_saldo)     
                
                if mostrar_cuentas == '2':
                    if debit or credit:

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
                            'activo': activo if activo else 0,
                            'pasivo': pasivo if pasivo else 0,
                            'deficit': deficit if deficit else 0,
                            'superavit': superavit if superavit else 0
                            })
                elif mostrar_cuentas == '3':
                    
                    if campo['type'] != 'view':
                        if debit or credit:

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
                                'activo': activo if activo else 0,
                                'pasivo': pasivo if pasivo else 0,
                                'deficit': deficit if deficit else 0,
                                'superavit': superavit if superavit else 0
                                })
                else:

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
                        'activo': activo if activo else 0,
                        'pasivo': pasivo if pasivo else 0,
                        'deficit': deficit if deficit else 0,
                        'superavit': superavit if superavit else 0
                        })
                # ----------reseteo de variables-------------

                deudores = 0
                acreedores = 0
                activo = 0
                pasivo = 0
                deficit = 0
                superavit = 0
            
            #debit y credito
            if (s_debit - s_credit) < 0:
                s_d_debit = (s_debit - s_credit)*-1
            else:
                s_d_credit = (s_debit - s_credit)
            s_i_debit = (s_debit + s_d_debit)   
            s_i_credit = (s_credit + s_d_credit)
                
            #deudores y acreedores  
            if (s_deudores - s_acreedores) < 0:
                s_d_deudores = (s_deudores - s_acreedores)*-1
            else:
                s_d_acreedores = (s_deudores - s_acreedores)
            s_i_deudores = (s_deudores + s_d_deudores)      
            s_i_acreedores = (s_acreedores + s_d_acreedores)
                
            #activo y pasivo    
            if (s_activo - s_pasivo) < 0:
                s_d_activo = (s_activo - s_pasivo)*-1
            else:
                s_d_pasivo = (s_activo - s_pasivo)  
            s_i_activo = (s_activo + s_d_activo)            
            s_i_pasivo = (s_pasivo + s_d_pasivo)    
                
            #deficit y superavit    
            if (s_deficit - s_superavit) < 0:
                s_d_deficit = (s_deficit - s_superavit)*-1
            else:
                s_d_superavit = (s_deficit - s_superavit)   
            s_i_deficit = (s_deficit + s_d_deficit)
            s_i_superavit = (s_superavit + s_d_superavit)

            result_resumen.append({
                's_debit': s_debit if s_debit else 0,
                's_credit': s_credit if s_credit else 0,
                's_d_debit': s_d_debit if s_d_debit else 0,
                's_d_credit': s_d_credit if s_d_credit else 0,
                's_i_debit': s_i_debit if s_i_debit else 0,
                's_i_credit': s_i_credit if s_i_credit else 0,
                's_deudores': s_deudores if s_deudores else 0,
                's_acreedores': s_acreedores if s_acreedores else 0,
                's_d_deudores': s_d_deudores if s_d_deudores else 0,
                's_d_acreedores': s_d_acreedores if s_d_acreedores else 0,
                's_i_deudores': s_i_deudores if s_i_deudores else 0,
                's_activo': s_activo if s_activo else 0,
                's_i_acreedores': s_i_acreedores if s_i_acreedores else 0,
                's_pasivo': s_pasivo if s_pasivo else 0,
                's_d_activo': s_d_activo if s_d_activo else 0,
                's_d_pasivo': s_d_pasivo if s_d_pasivo else 0,
                's_i_activo': s_i_activo if s_i_activo else 0,
                's_i_pasivo': s_i_pasivo if s_i_pasivo else 0,
                's_deficit': s_deficit if s_deficit else 0,
                's_superavit': s_superavit if s_superavit else 0,
                's_d_deficit': s_d_deficit if s_d_deficit else 0,
                's_d_superavit': s_d_superavit if s_d_superavit else 0,
                's_i_deficit': s_i_deficit if s_i_deficit else 0,
                's_i_superavit': s_i_superavit if s_i_superavit else 0
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
                    for sumar in ['saldo_inicial', 'debit', 'credit', 'deudores', 'acreedores', 'activo', 'pasivo', 'deficit', 'superavit']:
                        detalle_code[code][sumar] += detalle[sumar]

            aux_detalle = []
            for code in detalle_code:
                aux_detalle.append(detalle_code[code])

            if not resumen:
                resumen = plan['resumen'][0]
            else:
                for campo in plan['resumen'][0]:
                    resumen[campo] += plan['resumen'][0][campo]

        ret = [{
            'detalle': [{}],
            'resumen': [{}],
        }]
        ret[0]['detalle'] = sorted(aux_detalle, key=lambda var: var['parent_left'])
        ret[0]['resumen'][0] = resumen

        return ret
