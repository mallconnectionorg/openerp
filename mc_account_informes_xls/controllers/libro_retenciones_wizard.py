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

from report import report_sxw
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

import calendar
import time, re, pprint, pytz
import datetime

class libro_retenciones_wizard(osv.osv):

    _name = 'libro.retenciones.wizard'

    def get_detalle(self, cr, uid, form):
        
        compania_id = int(form['compania_id'])
        periodos = int(form['periodo_id'])

        sql_retenciones = """
            SELECT
            "account_invoice"."id",
            "account_invoice"."internal_number",
            "account_invoice"."supplier_invoice_number",
            "account_invoice"."company_id",
            "account_invoice"."partner_id",
            "account_invoice"."amount_tax",
            "account_invoice"."type",
            "account_invoice"."state",
            "account_invoice"."date_invoice",
            "account_invoice"."period_id",
            "account_invoice"."amount_untaxed",
            "res_partner"."name" name_partner,
            "res_partner"."rut" vat_partner,
            "account_period"."date_stop",
            "account_period"."date_start",
            "account_move"."name" as comprobante,
            "account_move"."date" as fecha_comprobante,
            EXTRACT(day FROM account_move.date) AS "dia_comprobante"  
            FROM
            "res_partner" INNER JOIN "account_invoice" ON "res_partner"."id" = "account_invoice"."partner_id"
            INNER JOIN "account_period" ON "account_invoice"."period_id" = "account_period"."id"
            INNER JOIN "account_move" ON "account_invoice"."move_id" = "account_move"."id"
            WHERE
            "account_invoice"."type" IN ('in_invoice','in_refund')
            AND (select account_journal.sii_codigo from account_journal where account_journal.id="account_invoice"."journal_id") = '0BH'
            AND "account_invoice"."state" in ('open','paid')
            AND "account_invoice"."company_id" = '%s'
            AND "account_invoice"."period_id" = '%s'
            order by EXTRACT(year FROM date_invoice) desc ,EXTRACT(month FROM date_invoice) desc ,EXTRACT(day FROM date_invoice) asc 
            """
        
        # Obtención de Datos - Compras
        cr.execute(sql_retenciones % (compania_id, periodos))
        recordset_retenciones = cr.dictfetchall()
        
        
        result_retenciones = []
        result_final = []

        saldo_amount_untaxed = 0
        saldo_amount_exento = 0
        saldo_amount_tax = 0
        saldo_amount_other_tax = 0
        saldo_amount_total = 0
        

        
        for campo in recordset_retenciones:
        
            if campo.has_key('type') and campo['type'] == 'in_refund':
                saldo_amount_untaxed = float(campo['amount_untaxed']*-1)
                saldo_amount_tax = float(campo['amount_tax']*-1)

            else:
                saldo_amount_untaxed = float(campo['amount_untaxed'])
                saldo_amount_tax = float(campo['amount_tax'])

            result_retenciones.append({
                'comprobante': (campo['comprobante']) if campo.has_key('comprobante') else '-',
                'dia_comprobante': (campo['dia_comprobante']) if campo.has_key('dia_comprobante') else '-',
                'date_invoice': (campo['date_invoice']) if campo.has_key('date_invoice') else '-',
                'vat_partner': self.format_rut(campo['vat_partner'],'cl'),
                'name_partner': (campo['name_partner']) if campo.has_key('name_partner') else '-',
                'supplier_invoice_number': (campo['supplier_invoice_number']) if campo.has_key('supplier_invoice_number') else '-',
                'saldo_amount_untaxed': saldo_amount_untaxed if saldo_amount_untaxed else '0',
                'saldo_amount_tax': saldo_amount_tax if saldo_amount_tax else '0',
                })
            #reseteo de variables
            saldo_amount_untaxed = 0
            saldo_amount_tax = 0
            
    #--- totales compras
        total_amount_untaxed = 0
        total_amount_tax = 0
        contador = 0

        for campos in result_retenciones:
            total_amount_untaxed += float(campos['saldo_amount_untaxed'])
            total_amount_tax += float(campos['saldo_amount_tax'])
            contador += 1 
        


        result_final.append({
            'detalle': result_retenciones,
            'total_amount_untaxed': total_amount_untaxed,
            'total_amount_tax': total_amount_tax,
            'contador': contador,
            })


        return result_final
        
        
    #formateador de rut
    def format_rut(self, rut, cod_pais):
        if rut:
            #quitar el "cl"
            vat=re.sub(str(cod_pais), "", rut)
            if vat=='19': return str(vat)[-2:-1]+'-'+str(vat)[-1:]
            vat = vat.replace("-","")
            vat=str(vat)[-9:-7]+'.'+str(vat)[-7:-4]+'.'+str(vat)[-4:-1]+'-'+str(vat)[-1:]
            #vat.format('-','.','.')
            return vat
        else:
            return {}
