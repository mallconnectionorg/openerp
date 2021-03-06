##!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Pedro Arroyo M <parroyo@mallconnection.com>
#   Copyright (C) 2015 Mall Connection(<http://www.mallconnection.org>).
#
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


from openerp.osv import osv

class hr_payslip_employees(osv.osv_memory):

    _inherit ='hr.payslip.employees'
    
    def compute_sheet(self, cr, uid, ids, context=None):
        run_pool = self.pool.get('hr.payslip.run')
        if context is None:
            context = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['pension_indicators_id'])
        pension_indicators_id =  run_data.get('pension_indicators_id', False)
        pension_indicators_id = pension_indicators_id and pension_indicators_id[0] or False
        if pension_indicators_id: context.update({'pension_indicators_id': pension_indicators_id})
        return super(hr_payslip_employees, self).compute_sheet(cr, uid, ids, context=context)

hr_payslip_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
