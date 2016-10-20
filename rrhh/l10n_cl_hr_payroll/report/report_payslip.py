#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
from l10n_cl_hr_payroll.report  import amount_to_text_es
from hr_payroll.report import report_payslip

class payslip_report(report_payslip.payslip_report):

    def __init__(self, cr, uid, name, context):
        super(payslip_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'disclaimer': self.disclaimer})
        
    def disclaimer(self, payslip, cur):
        line_ids = payslip.line_ids
        company_name = payslip.contract_id.company_id.name
        amount = 0
        if line_ids:            
                amount =  sum([line.total for line in  line_ids if line.code == 'liquido'])  
                     
        text = 'Certifico que he recibido de ' + company_name + ' a mi entera satisfaccion la cantidad de '
        text = text + amount_to_text_es.amount_to_text(amount, 'es', cur)
        text = text + ' indicado  en la presente liquidacion y no tengo cargo ni cobro alguno que hacer por ninguno de los conceptos correspondidos en ella.'
        return text
 

from netsvc import Service
del Service._services['report.payslip']


report_sxw.report_sxw('report.payslip', 'hr.payslip', 'l10n_cl_hr_payroll/report/report_payslip.rml', parser=payslip_report)