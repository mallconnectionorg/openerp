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

from calendar import monthrange

class libro_mayor_wizard(osv.osv):

    _name = 'libro.mayor.wizard'

    def get_detalle(self, cr, uid, form):
        
        period_obj = self.pool.get('account.period')
        
        compania_id = int(form['compania_id'])
        company_ids = compania_id
        #periodos = int(form['periodo_id'])
        
        periodo_desde = period_obj.browse(cr, uid, int(form['periodo_id']))
        
        if form['periodo_hasta_id']:
            periodo_hasta = period_obj.browse(cr, uid, int(form['periodo_hasta_id']))
        else:
            periodo_hasta = False

        ano_contable = periodo_desde.fiscalyear_id.code
        ano_contable_id = periodo_desde.fiscalyear_id.id
        
        fecha_inicial_anho = periodo_desde.fiscalyear_id.date_start
        fecha_hasta_anho = periodo_desde.fiscalyear_id.date_stop
        
        fecha_desde = periodo_desde.date_start
        
        if periodo_hasta:
            fecha_hasta = periodo_hasta.date_stop
        else:
            fecha_hasta = periodo_desde.date_stop

        sql_balance_periodo = """
        SELECT
        aa.id AS account_id,
        aa.code,
        aa.name,
        (
            SELECT 
            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance_inicial
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=aa.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id %s AND special)  --periodos seleccionados
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
        ) as balance_inicial,
        (
            SELECT 
            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance_anterior
            FROM 
            account_move_line l 
            WHERE 
            l.account_id IN (select n.id from account_account as n,account_account as n2 where n2.id=aa.id and n.parent_left BETWEEN n2.parent_left and n2.parent_right) --ids cuentas del plan de cuentas
            AND l.state <> 'draft' --estado del movimiento
            %s
            AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted')  --estado del comprobante
        ) as balance_anterior
        FROM
        account_account aa RIGHT JOIN account_move_line aml ON aml.account_id = aa.id
        WHERE
        %s
        AND aml.company_id IN (%s)
        %s
        GROUP BY
        aa.code,
        aa.name,
        aa.id
        ORDER BY
        aa.code
        """
        
        
        sql_detalles = """
        SELECT
        aml.id,
        aml.date,
        EXTRACT(day FROM aml.date) AS date_day,
        EXTRACT(month FROM aml.date) AS date_month,
        aml.name AS glosa,
        aml.ref,
        aml.debit,
        aml.credit,
        (select date_due from account_invoice ai where ai.move_id=aml.move_id) AS date_due,
        (select name from account_move where id=aml.move_id) as compte,
        rp.name,
        rp.rut
        FROM
        account_account aa RIGHT JOIN account_move_line aml ON aml.account_id = aa.id LEFT JOIN res_partner rp ON aml.partner_id=rp.id
        WHERE
        aml.account_id = '%s'
        %s
        ORDER BY
        aml.date
        """

        #fecha_inicial_anho = datetime.date(ano_contable,1,1)
        #fecha_hasta_anho = datetime.strptime(fecha_desde, "%Y-%m-%d")-datetime.timedelta(days=1)
        #fecha_hasta_anho = datetime.date(fecha_hasta_anho.year,fecha_hasta_anho.month,fecha_hasta_anho.day)
            
        balance_inicial = "='" + str(ano_contable_id) + "'"
        balance_anterior = "AND l.date BETWEEN '" + str(fecha_inicial_anho) + "' AND '" + str(fecha_hasta_anho) + "'"
        where_periodo = "aml.date BETWEEN '" + fecha_desde + "' AND '" + fecha_hasta + "'"
        where_grupo = ""
        cr.execute(sql_balance_periodo % (balance_inicial, balance_anterior, where_periodo, company_ids, where_grupo))
        recordset_libro_mayor = cr.dictfetchall()
        
        result_mayor_periodo = []
        result_detalles = []
        result_totales_y_resumen = []
        
        suma_total_debit = 0
        suma_total_credit = 0
        suma_total_saldo = 0
        
        for campo in recordset_libro_mayor:
            saldo_inicial = float(campo['balance_inicial']) + float(campo['balance_anterior'])

            #reseteo de "result_detalles"
            suma_debit = 0
            suma_credit = 0
            suma_saldo = 0
            result_detalles = []
            #----------------------------- Obtención de Datos - Detalles ----------------------
            if campo['account_id']:
                id_cuenta = campo['account_id']
                

                where2 = "AND aml.date BETWEEN '" + fecha_desde + "' AND '" + fecha_hasta + "'"
                cr.execute(sql_detalles % (id_cuenta,where2))
                recordset_detalles = cr.dictfetchall()
                
                saldo=saldo_inicial
                for detalle in recordset_detalles:
                    
                    fecha = str(int(detalle['date_day'])) +"-"+ str(int(detalle['date_month'])).zfill(2)
                    
                    saldo += float(detalle['debit']) - float(detalle['credit'])
                    
                    result_detalles.append({
                        'date':detalle['date'],
                        'fecha':fecha,
                        'compte' : (detalle['compte']) if detalle.has_key('compte') else '-',
                        'name' : (detalle['name']) if detalle.has_key('name') else '-',
                        'rut' : self.format_rut(detalle['rut']),
                        'glosa' : (detalle['glosa']) if detalle.has_key('glosa') else '-',
                        'ref' : (detalle['ref']) if detalle.has_key('ref') else '-',
                        'date_due' : (detalle['date_due']) if detalle.has_key('date_due') else '-',
                        'debit' : (detalle['debit']) if detalle.has_key('debit') else '-',
                        'credit' : (detalle['credit']) if detalle.has_key('credit') else '-',
                        'saldo' : saldo
                        })
                    suma_debit += detalle['debit']
                    suma_credit += detalle['credit']
                    suma_saldo += saldo
                
            #---------------------------FIN Obtención de Datos - Detalles ----------------------            
            espacio = 'espacio'     
            result_mayor_periodo.append({
                'code': (campo['code']) if campo.has_key('code') else '-',
                'name': (campo['name']) if campo.has_key('name') else '-',  
                'saldo_inicial': saldo_inicial,
                'detallee': result_detalles,
                'suma_debit' : suma_debit,
                'suma_credit' : suma_credit,
                #'suma_saldo' : saldo_inicial+(suma_debit-suma_credit),
                'espacio':espacio
                })  
        
            suma_total_debit += suma_debit
            suma_total_credit += suma_credit
            suma_total_saldo += suma_saldo

        result_totales_y_resumen.append({
            'detalle': result_mayor_periodo,
            'suma_total_debit' : suma_total_debit,
            'suma_total_credit' : suma_total_credit,
            'suma_total_saldo' : suma_total_saldo
            })
        return result_totales_y_resumen
        
    def format_rut(self, rut):
        if rut:
            rut = rut.replace('.','').replace('-','').replace('cl','').upper()
            return "{:n}".format(int(rut[:-1])) + '-' + rut[-1]
        else:
            return {}

