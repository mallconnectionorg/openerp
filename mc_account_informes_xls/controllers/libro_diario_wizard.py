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

class libro_diario_wizard(osv.osv):

    _name = 'libro.diario.wizard'

    def get_detalle(self, cr, uid, form):
        
        compania_id = int(form['compania_id'])
        periodos = int(form['periodo_id'])
        
        sql_balance_periodo = """
        SELECT
        am.id AS move_id,
        am.name,
        am.date,
        aj.name AS name_journal
        FROM
        account_journal aj RIGHT JOIN account_move am ON am.journal_id=aj.id INNER JOIN account_invoice ai ON am.id=ai.move_id
        WHERE
        ai.period_id in (%s)
        ORDER BY
        am.date
        """
        
        sql_detalles = """
        SELECT
        aa.code,
        aa.name AS account_name,
        aml.debit,
        aml.credit,
        aml.name,
        aml.ref,
        ai.date_due
        FROM
        account_account aa RIGHT JOIN account_move_line aml ON aml.account_id=aa.id LEFT JOIN account_move am ON aml.move_id=am.id LEFT JOIN account_invoice ai ON am.id=ai.move_id
        WHERE
        am.id = '%s'
        AND ai.period_id in (%s)
        """

        cr.execute(sql_balance_periodo % (periodos))
        recordset_libro_mayor = cr.dictfetchall()
        
        result_mayor_periodo = []
        result_detalles = []
        result_totales_y_resumen = []
        
        suma_total_debit = 0
        suma_total_credit = 0
        
        for campo in recordset_libro_mayor:

            suma_debit = 0
            suma_credit = 0
            result_detalles = []
            if campo['move_id']:
                move_id = campo['move_id']
                cr.execute(sql_detalles % (move_id, periodos))
                recordset_detalles = cr.dictfetchall()
                
                for detalle in recordset_detalles:
                    
                    result_detalles.append({
                        'code' : (detalle['code']) if detalle.has_key('code') else '-',
                        'account_name' : (detalle['account_name']) if detalle.has_key('account_name') else '-',
                        'debit' : (detalle['debit']) if detalle.has_key('debit') else 0,
                        'credit' : (detalle['credit']) if detalle.has_key('credit') else 0,
                        'name' : (detalle['name']) if detalle.has_key('name') else '-',
                        'ref' : (detalle['ref']) if detalle.has_key('ref') else '-',
                        'date_due' : (detalle['date_due']) if detalle.has_key('date_due') else '-',
                        })
                    suma_debit += int(detalle['debit'])
                    suma_credit += int(detalle['credit'])
            espacio = 'espacio'
            result_mayor_periodo.append({
                'name': (campo['name']) if campo.has_key('name') else '-',  
                'date': (campo['date']) if campo.has_key('date') else '-',  
                'name_journal': (campo['name_journal']) if campo.has_key('name_journal') else '-',
                'detallee': result_detalles,
                'suma_debit': suma_debit,
                'suma_credit': suma_credit,
                'espacio':espacio
                })  
                
            suma_total_debit += suma_debit
            suma_total_credit += suma_debit
        
        result_totales_y_resumen.append({
            'detalle': result_mayor_periodo,
            'suma_total_debit': suma_total_debit,
            'suma_total_credit': suma_total_credit
            })
        return result_totales_y_resumen
