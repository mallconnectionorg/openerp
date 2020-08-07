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

class inventario_y_balance_wizard(osv.osv):
    
    _name = 'inventario.y.balance.wizard'


    def get_detalle(self, cr, uid, form):
    
        #---------------- NEW
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

            mes_contable = form['mes_contable'][1]
            mes_contable = period_obj.search(cr, SUPERUSER_ID, [('name', '=', mes_contable), ('company_id', '=',plan_cuenta.company_id.id)])[0]
            ano_contable = period_obj.browse(cr, uid, mes_contable).fiscalyear_id.id
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
            SELECT
                min(l.account_id)
            FROM
                account_move_line l
            WHERE
                l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=principal.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
                AND l.state <> 'draft' --estado del movimiento
                AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s')  --periodos seleccionados
                AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
            ) as id_cuentas,
            (
            SELECT name FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s'
            ) as nombre_periodo
            FROM account_account principal
            where principal.level >= 1 and principal.level <= '%s'
            order by parent_left
            """

            sql_detalles = """
            select
            sum(l.debit) as debit,
            sum(l.credit) as credit,
            l.partner_id,
            res_partner.name,
            res_partner.rut,
            a.code
            from
            account_account a right join account_move_line l on l.account_id=a.id left join res_partner on l.partner_id = res_partner.id
            where
            l.account_id='%s'
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = '%s' AND id = '%s')  --periodos seleccionados
            group by
            a.code,
            l.partner_id,
            res_partner.name,
            res_partner.rut
            ORDER BY res_partner.name
            """

            # Obtención de Datos - Balance
            cr.execute(sql_balance_periodo % (plan_cuenta, ano_contable, ano_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable,nivel))
            recordset_balance_periodo = self.cr.dictfetchall()

            result_balance_periodo = []
            result_detalles = []
            result_resumen = []

            parcial = 0
            parcial_total = 0

            saldo_inicial = 0
            calcular_saldo = 0
            deudores = 0
            acreedores = 0
            activo = 0
            pasivo = 0
            deficit = 0
            superavit = 0
            #debit
            s_debit = 0
            s_d_debit = 0
            s_i_debit = 0
            #credit
            s_credit = 0
            s_d_credit = 0
            s_i_credit = 0
            #deudores
            s_deudores = 0
            s_d_deudores = 0
            s_i_deudores = 0
            #acreedores
            s_acreedores = 0
            s_d_acreedores = 0
            s_i_acreedores = 0
            #activo
            s_activo = 0
            s_d_activo = 0
            s_i_activo = 0
            #pasivo
            s_pasivo = 0
            s_d_pasivo = 0
            s_i_pasivo = 0
            #deficit
            s_deficit = 0
            s_d_deficit = 0
            s_i_deficit = 0
            #superavit
            s_superavit = 0
            s_d_superavit = 0
            s_i_superavit = 0
            # ----------FIN para el resumen del balance de 8 columnas-------------

            # ----------resumen balance de 8 columnas-------------

            # Obtención de Datos - Nivel 6 - para que las sumas no cambien cuando se cambia de nivel
            cr.execute(sql_balance_periodo % (plan_cuenta, ano_contable, ano_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable, ano_contable, mes_contable,6))
            recordset_balance_nivel_6 = self.cr.dictfetchall()

            for campo in recordset_balance_nivel_6:
                saldo_inicial_debit = float(campo['balance_inicial_debit']) + float(campo['balance_anterior_debit'])
                saldo_inicial_credit = float(campo['balance_inicial_credit']) + float(campo['balance_anterior_credit'])

                #dejar saldo inicial en debit o credit
                debit=float(campo['debit']) + saldo_inicial_debit
                credit=float(campo['credit']) + saldo_inicial_credit

                calcular_saldo = debit - credit

                if calcular_saldo < 0:
                    deudores = abs(calcular_saldo)
                else:
                    acreedores = abs(calcular_saldo)

                if campo['code'][:1] == '1':
                    activo = abs(calcular_saldo)
                elif campo['code'][:1] in ['2','3']:
                    pasivo = abs(calcular_saldo)
                elif campo['code'][:1] in ['5','6']:
                    deficit = abs(calcular_saldo)
                elif campo['code'][:1] in ['4','7']:
                    superavit = abs(calcular_saldo)

                if campo['type'] and campo['type'] != 'view':
                    s_debit += float(campo['debit'])
                    s_credit += float(campo['credit'])
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

            if (s_debit - s_credit) < 0:
                s_d_debit = (s_debit - s_credit)*-1
            else:
                s_d_credit = (s_debit - s_credit)
            s_i_debit = (s_debit + s_d_debit)
            s_i_credit = (s_credit + s_d_credit)

            if (s_deudores - s_acreedores) < 0:
                s_d_deudores = (s_deudores - s_acreedores)*-1
            else:
                s_d_acreedores = (s_deudores - s_acreedores)
            s_i_deudores = (s_deudores + s_d_deudores)
            s_i_acreedores = (s_acreedores + s_d_acreedores)

            if (s_activo - s_pasivo) < 0:
                s_d_activo = (s_activo - s_pasivo)*-1
            else:
                s_d_pasivo = (s_activo - s_pasivo)
            s_i_activo = (s_activo + s_d_activo)
            s_i_pasivo = (s_pasivo + s_d_pasivo)

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

                if campo['code'][:1] == '1':
                    activo = abs(calcular_saldo)
                elif campo['code'][:1] in ['2','3']:
                    pasivo = abs(calcular_saldo)
                elif campo['code'][:1] in ['5','6']:
                    deficit = abs(calcular_saldo)
                elif campo['code'][:1] in ['4','7']:
                    superavit = abs(calcular_saldo)

                parcial = 0
                result_detalles = []
            #----------------------------- Obtención de Datos - Detalles ----------------------
                if campo['id_cuentas'] and campo['type']!='view':
                    id_cuenta = campo['id_cuentas']
                    cr.execute(sql_detalles % (id_cuenta, ano_contable, mes_contable))
                    recordset_detalles = self.cr.dictfetchall()

                    for detalle in recordset_detalles:

                        calcular_saldo_2 = float(detalle['debit']) - float(detalle['credit'])
                        if calcular_saldo_2 < 0:
                            deudores_2 = calcular_saldo_2
                            acreedores_2 = 0
                        else:
                            deudores_2 = 0
                            acreedores_2 = calcular_saldo_2

                        result_detalles.append({
                            'partner_id' : detalle['partner_id'],
                            'rut' : self.format_rut(detalle['rut']),
                            'name' : (detalle['name']) if detalle.has_key('name') else '-',
                            'debit' : (detalle['debit']) if detalle.has_key('debit') else '-',
                            'credit' : (detalle['credit']) if detalle.has_key('credit') else '-',
                            'deudores' : abs(deudores_2),
                            'acreedores' : abs(acreedores_2)
                            })
                        parcial += (abs(deudores_2) - abs(acreedores_2))

                if mostrar_cuentas == '2':
                    if campo['debit'] or campo['credit'] > 0:

                        parcial_total = deudores if deudores else acreedores

                        result_balance_periodo.append({
                            'parent_left': parent_left[campo['code']],
                            'type': (campo['type']) if campo.has_key('type') else '-',
                            'id_cuentas': (campo['id_cuentas']) if campo.has_key('id_cuentas') else '-',
                            'level': (campo['level']) if campo.has_key('level') else '0',
                            'code': (campo['code']) if campo.has_key('code') else '-',
                            'name': (campo['name']) if campo.has_key('name') else '-',
                            'saldo_inicial': saldo_inicial if saldo_inicial else 0,
                            'debit': (campo['debit']) if campo.has_key('debit') else 0,
                            'credit': (campo['credit']) if campo.has_key('credit') else 0,
                            'deudores': abs(deudores) if deudores else 0,
                            'acreedores': acreedores if acreedores else 0,
                            'activo': activo if activo else 0,
                            'pasivo': pasivo if pasivo else 0,
                            'deficit': deficit if deficit else 0,
                            'superavit': superavit if superavit else 0,
                            'parcial':parcial if parcial else 0,
                            'parcial_total':parcial_total if parcial_total else 0,
                            'detallee': result_detalles,
                            })
                else:

                        parcial_total = deudores if deudores else acreedores

                        result_balance_periodo.append({
                            'parent_left': parent_left[campo['code']],
                            'type': (campo['type']) if campo.has_key('type') else '-',
                            'level': (campo['level']) if campo.has_key('level') else '0',
                            'code': (campo['code']) if campo.has_key('code') else '-',
                            'name': (campo['name']) if campo.has_key('name') else '-',
                            'saldo_inicial': saldo_inicial if saldo_inicial else 0,
                            'debit': (campo['debit']) if campo.has_key('debit') else 0,
                            'credit': (campo['credit']) if campo.has_key('credit') else 0,
                            'deudores': abs(deudores) if deudores else 0,
                            'acreedores': acreedores if acreedores else 0,
                            'activo': activo if activo else 0,
                            'pasivo': pasivo if pasivo else 0,
                            'deficit': deficit if deficit else 0,
                            'superavit': superavit if superavit else 0,
                            'parcial':parcial if parcial else 0,
                            'parcial_total':parcial_total if parcial_total else 0,
                            'detallee': result_detalles,
                            })

                deudores = 0
                acreedores = 0
                activo = 0
                pasivo = 0
                deficit = 0
                superavit = 0

            result_balance_totales_y_resumen.append({
                'detalle': result_balance_periodo,
                'resumen': result_resumen,
                })
        #-NEW
        resumen = False
        detalle_code = {}
        partner_ids = {}
        for plan in result_balance_totales_y_resumen:

            for detalle in plan['detalle']:
                code = detalle['code']
                
                if code not in detalle_code:
                    detalle_code[code] = detalle
                else:
                    for sumar in ['saldo_inicial', 'debit', 'credit', 'deudores', 'acreedores', 'activo', 'pasivo', 'deficit', 'superavit', 'parcial', 'parcial_total']:
                        detalle_code[code][sumar] += detalle[sumar]
                
                if code not in partner_ids:
                    partner_ids[code] = {}
                for detallee in detalle['detallee']:
                    partner_id = detallee['partner_id']
                    
                    if partner_id not in partner_ids[code]:
                        partner_ids[code][partner_id] = detallee
                    else:
                        for sumar in ['debit', 'credit', 'deudores', 'acreedores']:
                            partner_ids[code][partner_id][sumar] += detallee[sumar]

            aux_detalle = []
            for code in detalle_code:
                aux_partner_id = []
                detalle_code[code]['detallee'] = []
                for partner_id in partner_ids[code]:
                    detalle_code[code]['detallee'].append(partner_ids[code][partner_id])
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

        self.result_balance_totales_y_resumen = ret
        return ret

    def format_rut(self, rut):
        if rut:
            rut = rut.replace('.','').replace('-','').replace('cl','').upper()
            return "{:n}".format(int(rut[:-1])) + '-' + rut[-1]
        else:
            return {}
