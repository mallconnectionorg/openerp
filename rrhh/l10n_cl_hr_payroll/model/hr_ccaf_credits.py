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

from osv import osv
from osv import fields
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

class hr_ccaf_credits(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.ccaf.credits'
    _description = 'hr.ccaf.credits'
 
    def _get_state(self, cr, uid, ids, name, arg, context=None):
        res = {}
        this = self.browse(cr,uid,ids)[0]
        inv_count = [1 for item in this.credit_line_ids if item.invoiced] 
        if sum(inv_count)==0:
            state ='active'
        elif sum(inv_count)>0:
            state='invoicing'
        elif sum(inv_count)>=len(this.credit_line_ids):
            state='done'
        else:
            state='active'
        res[ids[0]] = state

        return res
    
    _columns = {
            'name':fields.char('name', size=64, required=True),
            #'code':fields.char('Code', size=64, required=True),
            'type':fields.selection([
                ('personal','Personal credit'),
                ('dental','Dental credit'),
                ('leasing','Leasing credit'),                
                ('life_insurance','Life insurance credit'),
                 ],    'Credits type', select=True, required=True),
            'payment_term': fields.integer('Payment term', required=True) ,
            'current_payment': fields.integer('Current payment', required=True) ,
            'amount': fields.float('Amount', required=True),
            'employee_id':fields.many2one('hr.employee', 'Employee', required=False), 
            #'state':fields.selection([
            #    ('active','Active'),
            #    ('inactive','Inactive'),
            #     ],    'State', select=True, readonly=True),
            'state': fields.function(_get_state, string='Status', type='selection', selection=[
                ('active','Active'),
                ('invoicing','Invoicing'),
                ('done','Done'),
                 ], readonly=False),
            'credit_line_ids':fields.one2many('hr.ccaf.credits.line', 'credits_id', 'Credit line', ondelete='cascade'),
        }
    
    _defaults = {  
        'state': 'active',  
        }
    
    #def unlink(self, cr, uid, ids, context=None):
    #    for t in self.read(cr, uid, ids, ['state'], context=context):
    #        if t['state'] not in ('done', 'invoicing'):
    #            raise osv.except_osv(_('Invalid Action!'), _('Cannot delete credit(s) which are already invoicing.'))
    #    return super(hr_ccaf_credits, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if not 'from_button' in context:
            vals.update(self.calc_quotes(cr, uid, ids, context))
        res = super(hr_ccaf_credits, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def create(self, cr,uid,vals, context=None):
        id = super(hr_ccaf_credits, self).create(cr, uid, vals, context=context)
        vals.update(self.calc_quotes(cr, uid, id, context=context))
        res = super(hr_ccaf_credits, self).write(cr, uid, id, vals, context=context)
        return res
        
    def calc_quotes(self, cr, uid, ids, context):
        this = self.browse(cr,uid,ids)
        try:
            if len(this)>0: this = this[0]
        
        except(Exception):
            pass
        
        quote = this.amount / this.payment_term
        line = {}
        if len(this.credit_line_ids)>0:
            self.pool.get('hr.ccaf.credits.line').unlink(cr,uid,[line_credit.id for line_credit in this.credit_line_ids],context)
        today = datetime.date.today()
          
        dinit = today + relativedelta(months=(this.current_payment-1)*-1)
        dinit = date(dinit.year,dinit.month,1)
        lines = []
        for i in range(this.payment_term):
            credit_line={}
            dpayment = dinit + relativedelta(months=i)
            credit_line['name']=dpayment.strftime("%d/%m/%Y")
            credit_line['date']=dpayment
            credit_line['amount']=quote
            credit_line['credits_id']=this.id
            lines.append([0,0,credit_line])
        
        c = {}   
        c['credit_line_ids'] = lines
        return c
        
    def button_calc_quotes(self, cr, uid, ids, context):
        c = self.calc_quotes(cr, uid, ids, context)
        context.update({'from_button':True})
        self.write(cr,uid,ids,c,context)
    
        
    def get_quote(self,cr,uid,ids,dt,context=None):
        fdt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
        this = self.browse(cr,uid,ids)[0]
        res = 0
        for line in this.credit_line_ids:
            ldt=datetime.datetime.strptime(line.date, "%Y-%m-%d").date()
            if date(ldt.year,ldt.month,1)==date(fdt.year,fdt.month,1):
                res = line.amount
        return res
    
    def get_invoiced(self,cr,uid,ids,dt,context=None):
        fdt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
        this = self.browse(cr,uid,ids)[0]
        res = 0
        for line in this.credit_line_ids:
            ldt=datetime.datetime.strptime(line.date, "%Y-%m-%d").date()
            if date(ldt.year,ldt.month,1)==date(fdt.year,fdt.month,1):
                res = line.invoiced
                break
        return res
hr_ccaf_credits()


class hr_ccaf_credits_line(osv.osv):
    _name = 'hr.ccaf.credits.line' 
    _columns = {
            'name':fields.char('Name', size=64, readonly=True),
            #TODO : import time required to get currect date
            'date': fields.date('Date',readonly=True),
            'amount': fields.float('Amount', digits=[12,2],readonly=True),
            'credits_id':fields.many2one('hr.ccaf.credits', 'credit', readonly=True), 
            'invoiced':fields.boolean('Invoiced', readonly=True), 
            'payslip_ref':fields.char('Payslip reference', readonly=True),
                    }
    _defaults = {  
        'invoiced': False,  
        }
    
hr_ccaf_credits_line()