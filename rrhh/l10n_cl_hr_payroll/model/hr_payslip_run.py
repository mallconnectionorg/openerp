#!/usr/bin/python
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

from osv import fields,osv



class hr_payslip_run(osv.osv):
    
    _name = 'hr.payslip.run' 
    _inherit = 'hr.payslip.run'
    #Do not touch _name it must be same as _inherit
    #_name = 'hr.payslip.run'
        
    _columns = {
            'pension_indicators_id':fields.many2one('hr.pension.indicators', 'Pension indicators', required=True), 
            
    } 
    
    def confirm_all(self, cr, uid, ids, context=None):
        payslip = self.pool.get('hr.payslip')
        payslips_objs = payslip.browse(cr, uid,\
            payslip.search(cr, uid, [('payslip_run_id','in',ids)], context=context), context=context)

        for payslip in payslips_objs:
            resp1 = payslip.hr_verify_sheet()
            if resp1:
                resp2 = payslip.process_sheet()
        return True
    

hr_payslip_run()