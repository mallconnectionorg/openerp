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
import time
from datetime import date, datetime
from openerp.tools.translate import _
from datetime import timedelta
from dateutil import relativedelta
import calendar

class hr_payslip(osv.osv):
    
    _name = 'hr.payslip' 
    _inherit = 'hr.payslip'
    #Do not touch _name it must be same as _inherit
    #_name = 'hr.payslip.run'
        
    _columns = {
            'pension_indicators_id':fields.many2one('hr.pension.indicators', 'Pension indicators', required=True), 
            
    } 
    
    def hr_verify_sheet(self, cr, uid, ids, context=None):
        res = super(hr_payslip, self).hr_verify_sheet(cr, uid, ids, context)
        this = self.browse(cr, uid, ids)[0]
        fdt = datetime.strptime(this.date_from, "%Y-%m-%d").date()
        ccaf_obj = self.pool.get('hr.ccaf.credits')
        for input in this.input_line_ids:
            linput = input.code.split('_')
            if len(linput)>0:
                if linput[0]=="ccaf":
                    ccaf = ccaf_obj.browse(cr,uid,int(linput[1]))
                    for item in ccaf.credit_line_ids:
                        ldt=datetime.strptime(item.date, "%Y-%m-%d").date()
                        if date(ldt.year,ldt.month,1)==date(fdt.year,fdt.month,1):
                            item.write({'invoiced':True, 'payslip_ref':this.number})
                            break

        return res

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'pension_indicators_id' in context:
            vals.update({'pension_indicators_id': context.get('pension_indicators_id')})  

        return super(hr_payslip, self).create(cr, uid, vals, context=context)
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res1 = False
            res2 = False
            res3 = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            
            if holiday_ids:
                holiday_obj = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0]
                res1 = holiday_obj.holiday_status_id.name
                res2 = holiday_obj.holiday_status_id.not_payable
                res3 = holiday_obj.holiday_status_id.justified
            return res1, res2, res3
        
#        def not_payable(employee_id, datetime_day, context=None):
#            res = False
#            day = datetime_day.strftime("%Y-%m-%d")
#            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
#            if holiday_ids:
#                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.not_payable
#            return res
        
        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                    #the employee had to work
                    leave_type, not_payable, justified = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    #not_payable = not_payable(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                                'not_payable': not_payable,
                                'justified': justified
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        if not contract.working_hours.var_attendance:
                            attendances['number_of_days'] += 1.0
                            attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
        return res
        
        #res = super(hr_payslip,self).get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context)
        
        
        #return res
    
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None): 
        res = super(hr_payslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context)
        
        for obj_contract in self.pool.get('hr.contract').browse(cr,uid,contract_ids):
            obj_employee = obj_contract.employee_id
            
            obj_pension_vol_discs = obj_employee.pension_vol_disc_ids
            obj_insurance = obj_employee.insurance_ids
            obj_ccaf_credits = obj_employee.ccaf_credits_ids
#            obj_bonuses = obj_contract.bonus_ids
            obj_fixed_allocations  = obj_contract.fixed_allocations_ids
            obj_invoices = obj_contract.invoice_ids
            

            if obj_fixed_allocations is not None:
                for fixed_allocations in obj_fixed_allocations:
                    input={}
                    
                    input['name'] = fixed_allocations.name or 'Fixed allocation'
                    input['code'] = fixed_allocations.allocation_type_id.code or 'fixed_allocations'
                    input['amount'] = fixed_allocations.amount
                    input['contract_id'] = obj_contract.id

                    res += [input]  
            
            if obj_pension_vol_discs is not None:   
                for penvoldisc in obj_pension_vol_discs:
                    input={}
                    
                    input['name'] = penvoldisc.name or 'apv'
                    input['code'] = penvoldisc.code or 'apv'
                    input['amount'] = penvoldisc.currency_id.compute(obj_contract.company_id.currency_id.id,penvoldisc.amount,
                                                              True,False,False,{'date':date_to}) if obj_contract.company_id else 0
                    input['contract_id'] = obj_contract.id
                    res += [input]                         
            
            if obj_insurance is not None:
                for insurance in obj_insurance:
                    input={}
                    
                    input['name'] = insurance.name or 'insurance'
                    input['code'] = insurance.code or 'insurance'
                    input['amount'] = insurance.currency_id.compute(obj_contract.company_id.currency_id.id,insurance.amount,
                                                              False,False,False,{'date':date_to})
                    input['contract_id'] = obj_contract.id
                    res += [input]    
    
            if obj_ccaf_credits is not None:
                i = 0
                for ccaf in obj_ccaf_credits:
                    if ccaf.get_invoiced(date_from): 
                        continue
                    input={}
                    
                    input['name'] = ccaf.name or 'ccaf'
                    input['code'] = "ccaf_"+str(ccaf.id)
                    input['amount'] = ccaf.get_quote(date_from)
                    input['contract_id'] = obj_contract.id
                    if input['amount']>0: 
                        res += [input] 
                    i+=1
                  
            if obj_invoices is not None:
                i=0
                for invoice in obj_invoices:
                    
                    input={}
                    sql = '''
    select debit from account_move_line 
    where move_id = %s
    and credit = 0 and EXTRACT(YEAR FROM date_maturity)= %s  and EXTRACT(month FROM date_maturity) = %s
                                ''' % (str(invoice.move_id.id),str(datetime.strptime(date_from, "%Y-%m-%d").year),str(datetime.strptime(date_from, "%Y-%m-%d").month))
                    cr.execute(sql)
                    res2 = cr.fetchall()
                    amount = 0
                    for r in res2:
                        amount= r[0]
                        
                    if amount>0:
                        input['name'] = invoice.number or 'invoice'
                        input['code'] = 'inv'+"_"+str(invoice.id)
                        input['amount'] = amount
                        input['contract_id'] = obj_contract.id
                        res += [input]   
                        i+=1
        return res    

    def get_taxable_stop(self,cr,uid,ids,employee,context):
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        taxable_stop = 0
        if employee.pension_scheme=="AFP":
            taxable_stop = obj_pension_indicators.rti_afp_added
        elif employee.pension_scheme=="ISP":
            taxable_stop = obj_pension_indicators.rti_ips_added
            
        return taxable_stop
    
    
    def _get_gratification(self, cr, uid,ids, accrued, context=None):
        
        res=0
        
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_contract = obj_payslip.employee_id.contract_id
        max_gratification = (obj_pension_indicators.rmi_employee_in_dependent * 4.75)/12

        if obj_contract.legal_gratification=='assessment_system':
            res=0   
                                                  
        elif obj_contract.legal_gratification=='25_payment_system':
            res=int(accrued*0.25)
            if res>max_gratification:
                res=max_gratification
        
        res = obj_currency.round(cr,uid,obj_clp,res)   
        return res
    
    def get_security_unemployee(self, cr, uid,ids, accrued, context=None):
        res = 0
        
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_employee = obj_payslip.employee_id
        obj_contract = obj_employee.contract_id
        taxable_stop = 0
          
        taxable_stop = obj_pension_indicators.rti_security_unemployee
        
        if accrued > taxable_stop:
            accrued = taxable_stop
        
        res = accrued * obj_contract.type_id.hr_afc_ids[0].employee_charge / 100 if len(obj_contract.type_id.hr_afc_ids)>0 else 0    
        
        res = obj_currency.round(cr,uid,obj_clp,res)   
        return res
    
    def get_security_unemployee_employer(self, cr, uid,ids, accrued, context=None):
        res = 0
        

        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_employee = obj_payslip.employee_id
        obj_contract = obj_employee.contract_id
        taxable_stop = 0
 
        taxable_stop = obj_pension_indicators.rti_security_unemployee
        
        if accrued > taxable_stop:
            accrued = taxable_stop
        
        res = accrued * obj_contract.type_id.hr_afc_ids[0].employer_charge / 100 if len(obj_contract.type_id.hr_afc_ids)>0 else 0          
            
        res = obj_currency.round(cr,uid,obj_clp,res)   
        return res
         
        
        
    def get_health(self, cr, uid,ids, accrued, context=None):
        
        res = 0
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_employee = obj_payslip.employee_id
        
        taxable_stop = 0
        health_percent = obj_pension_indicators.health_percent / 100
        
        taxable_stop = self.get_taxable_stop(cr, uid, ids, obj_employee, context)
        
        health_stop = taxable_stop * health_percent
        
        res = accrued * health_percent
        
        if res > health_stop:
            res = health_stop
            
        res = obj_currency.round(cr,uid,obj_clp,res)   
        return res
    
    def get_health_voluntary_discount(self, cr, uid,ids, accrued, context=None):
        
        res = self.get_health(cr, uid, ids, accrued, context)
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_employee = obj_payslip.employee_id
        agreed_quote = obj_employee.agreed_quote if obj_employee.agreed_quote else None
        
        if agreed_quote==None:
            return 0
        
        obj_currency = self.pool.get('res.currency')
        
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]

        obj_uf = self.pool.get('res.currency').search(cr, uid, [('name','=','UF')], context=context)
        obj_uf = self.pool.get('res.currency').browse(cr, uid, obj_uf, context=context)
        obj_uf = obj_uf[0]
        
        cnx = {'date': obj_pension_indicators.to or time.strftime('%Y-%m-%d')}
               
        agreed_quote = obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, agreed_quote,True, cnx)
        
        if res < agreed_quote:
            res = agreed_quote-res
        else:
            res = 0
    
        return res
    
    
    def get_security(self, cr, uid,ids, accrued, context=None):
        
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_employee = obj_payslip.employee_id

        taxable_stop = self.get_taxable_stop(cr, uid, ids, obj_employee, context)
        
        if accrued > taxable_stop:
            accrued = taxable_stop
        
        accrued = accrued * obj_employee.security_institutions_id.total / 100 if obj_employee.security_institutions_id else 0
            
        accrued = obj_currency.round(cr,uid,obj_clp,accrued)   
        return accrued
    
    def get_sis(self, cr, uid,ids, accrued, context=None):
        
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_employee = obj_payslip.employee_id

        taxable_stop = self.get_taxable_stop(cr, uid, ids, obj_employee, context)
        
        if accrued > taxable_stop:
            accrued = taxable_stop
        
        accrued = accrued * obj_pension_indicators.sis / 100 if obj_employee.security_institutions_id else 0
            
        accrued = obj_currency.round(cr,uid,obj_clp,accrued)   
        return accrued      
 
    def get_single_tax(self, cr, uid,ids, taxable, context=None):
        
        res = 0
        
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_employee = obj_payslip.employee_id
        obj_contract = obj_employee.contract_id
        obj_single_taxs = obj_pension_indicators.hr_single_tax_ids
        obj_single_tax_period = [value for value in obj_single_taxs if value.period==obj_contract.schedule_pay]
        taxable_stop = 0
        
        taxable_stop = self.get_taxable_stop(cr, uid, ids, obj_employee, context)
        
        for obj_single_tax in obj_single_tax_period:
            #if obj_single_tax.period==obj_contract.schedule_pay:
            if obj_single_tax.from_ <= taxable < obj_single_tax.to_:
                res = (taxable*obj_single_tax.percent/100)-obj_single_tax.reduction
                break
    
        if res>taxable_stop:
            res=taxable_stop
            
        res = obj_currency.round(cr,uid,obj_clp,res)   
        return res
    
    def get_family_assignment(self, cr, uid,ids, context=None):
        res = 0
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_employee = obj_payslip.employee_id
        obj_pension_indicators = obj_payslip.pension_indicators_id
        obj_fam_ass = obj_pension_indicators.hr_family_assignment_ids
        
        for line_fam_ass in obj_fam_ass:
            if(obj_employee.stretch==line_fam_ass.name): 
                res = line_fam_ass.quantity
        return res
        
    def get_mutual_amount(self, cr, uid,ids, taxable, context=None):
        
        res=0
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_company = obj_payslip.employee_id.contract_id.company_id
        
        if obj_company.mutual_quote>0:
            res = taxable*obj_company.mutual_quote /100
        else:
            res=0
        
        return obj_currency.round(cr,uid,obj_clp,res)
    
    def get_ccaf_amount(self, cr, uid,ids, taxable, context=None):
        
        res=0
        obj_currency = self.pool.get('res.currency')
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        obj_payslip = self.browse(cr,uid,ids, context)[0]
        obj_company = obj_payslip.employee_id.contract_id.company_id
        obj_ccaf = obj_company.ccaf_id
        
        res = taxable*obj_ccaf.quote/100
        
        return obj_currency.round(cr,uid,obj_clp,res)    

    def ndaysmonth(self, cr, uid,ids, workday, context=None):
        
        
        payslips = self.browse(cr,uid,ids)
        res=0
        for payslip in payslips:
            
            day_from = datetime.strptime(payslip.date_from,"%Y-%m-%d")
            day_to = datetime.strptime(payslip.date_to,"%Y-%m-%d")
            val = calendar.monthrange(day_from.year,day_from.month)
            if val[1]>30: res = 30
            else: res = val[1]
            for wd in workday.dict:
                i = workday.dict[wd]
                if i.not_payable:
                    res = res - int(i.number_of_days or 0)
                
            
        return res
    
    def get_straight_week(self, cr, uid,ids, worked_days, bonus_amount, context=None):
        res = 0
        
        payslips = self.browse(cr,uid,ids)
        
        for payslip in payslips:
            
            day_from = datetime.strptime(payslip.date_from,"%Y-%m-%d")
            sunday_days = len([1 for i in calendar.monthcalendar(day_from.year, day_from.month) if i[6] != 0])
            first_day,month_len = calendar.monthrange(day_from.year, day_from.month)
            
            #holiday days
            holidays_ids= self.pool.get('resource.calendar.holiday').search(cr, uid,[])
            holidays_read = self.pool.get('resource.calendar.holiday').read(cr, uid, holidays_ids, ['date'])
            holiday_days = len([1 for i in holidays_read if datetime.strptime(i['date'],"%Y-%m-%d").month==day_from.month])
            justified_days = len([1 for i in worked_days.dict.values() if i.justified])
            sunday_worked = worked_days.SUNDAYWORK.number_of_days if 'SUNDAYWORK' in worked_days.dict else 0
            #sunday nowork days 
            sunday_nowork_days  = (sunday_days + holiday_days) - sunday_worked
            
            workable_month_days = month_len - sunday_days - holiday_days
            
            workable_month_days -= justified_days
            
            res = (bonus_amount / workable_month_days) * sunday_nowork_days
            
        return res
    
hr_payslip()

class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _description = "Leave Type"

    _columns = {
                'not_payable':fields.boolean('Is not payable', required=False), 
                'justified':fields.boolean('Is justified', required=False),
                }

class hr_payslip_worked_days(osv.osv):
    '''
    Payslip Worked Days
    '''

    _inherit = 'hr.payslip.worked_days'
    _description = 'Payslip Worked Days'
    _columns = {
        'not_payable':fields.boolean('Is not payable', required=False), 
        'justified':fields.boolean('Is justified', required=False),
    }

hr_payslip_worked_days()

