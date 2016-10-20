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



class hr_employee(osv.osv):
    """Update employee class"""
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _inp_rates = {
                'sss':{
                    '!ccaf,mutual':{'fonasa':26.79,'isapre':19.79},
                    'ccaf'        :{'fonasa':26.19,'isapre':19.79},
                    'mutual'      :{'fonasa':25.84,'isapre':18.84},
                    'ccaf,mutual' :{'fonasa':25.24,'isapre':18.84}
                
                    },
                'empart':{
                    '!ccaf,mutual':{'fonasa':29.79,'isapre':22.79},
                    'ccaf'        :{'fonasa':29.19,'isapre':22.79},
                    'mutual'      :{'fonasa':28.84,'isapre':21.84},
                    'ccaf,mutual' :{'fonasa':28.24,'isapre':21.84}
                
                    },
                'empub':{
                    '!ccaf,mutual':{'fonasa':26.57,'isapre':19.57},
                    'ccaf'        :{'fonasa':25.97,'isapre':19.57},
                    'mutual'      :{'fonasa':25.62,'isapre':18.62},
                    'ccaf,mutual' :{'fonasa':25.02,'isapre':18.62}
                
                    }
                }
    def __init__(self, pool, cr):
        """Add a new state value"""
        if not 'civil_attached' in dict(super(hr_employee, self)._columns['marital'].selection):
            super(hr_employee, self)._columns['marital'].selection.append(('civil_attached', 'Civil attached'))
            
        return super(hr_employee, self).__init__(pool, cr)
    def _calc_ex_regime_rate(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        currency_obj = self.pool.get('res.currency')
        #informacion segun http://www.ips.gob.cl/pensiones-y-tramites-96642/134-tasas-ex-cajas-regimen-antiguo
        
        res = {}
        for employee in self.browse(cr, uid, ids, context=context):
            if employee.health_institutions_ids:
                health_code = int(employee.health_institutions_ids.code) or 0
                security_type = employee.security_institutions_id.type
                contract_obj = self.pool.get('hr.contract')
                contract_obj = contract_obj.browse(cr,uid,contract_obj.search(cr,uid,[('employee_id','=',employee.id)]),context)
                
                if contract_obj: company_obj = contract_obj[0].company_id 
                else: return res
                if not security_type: return res
                
                benf='!ccaf,mutual'
                if company_obj.mutual_id and company_obj.ccaf_id:
                    benf = 'ccaf,mutual'
                elif company_obj.mutual_id:
                    benf = 'mutual'
                elif company_obj.ccaf_id:
                    benf = 'ccaf'
                else:
                    benf='!ccaf,mutual'
                
                health = 'fonasa' if health_code == 8 else 'isapre'
                   
                value = self._inp_rates[security_type][benf][health] or 0
            else:
                value = 0
            
            res[employee.id] =  value
        return res
    
    _columns = {
        'pension_scheme':fields.selection([
           ('AFP','AFP'),
           ('INP','IPS (Ex-INP)'),
           ('SIP','Sin Institución Previsional'),
             ],    'Pension scheme', select=True, readonly=False, ), 
        #'pension_scheme_id': fields.many2one('hr.pension.scheme', string='Pension scheme'),
        'identification_type':fields.selection([
            ('CI','Identity card'),
            ('passport','Passport'),
             ],    'Identification type', select=True, readonly=False),
        'security_institutions_id': fields.many2one('hr.security.institutions', string='Security Institutions', domain="[('pension_scheme','=',pension_scheme)]"),
        'health_institutions_ids': fields.many2one('hr.health.institutions', string='Health institutions'),  
        'affiliate_volunteer_id':fields.many2one('hr.family.responsibilities', string='Affiliate volunteer', domain="[('relationship','=','spouse')]", required=False),
        'afp_volunteer': fields.float('AFP volunteer',), 
        'count_2_volunteer': fields.float('Count 2 volunteer',), 
        'begin_quote_volunteer': fields.date('Begin quote volunteer',), 
        'end_quote_volunteer': fields.date('End quote volunteer',),
        'agreed_quote': fields.float('Agreed quote',digits=(3,3)), 
        'ex_regime_rate': fields.function(_calc_ex_regime_rate, method=True, type='float', string='Ex regime rate', store=True), 
        'agreed_quote_currency':fields.many2one('res.currency', string='Agreed quote currency', domain="[('name','in',['UF','CLP'])]"),
        'FUN':fields.char('FUN number', size=64, required=False, readonly=False, ),     
        'stretch':fields.selection([
            ('A','A stretch'),
            ('B','B stretch'),
            ('C','C stretch'),
            ('D','D stretch'),
             ], 'Stretch family asignment', select=True, readonly=False), 
        #Solicitud Subsidio Trabajador Joven
        #'pension_worker':fields.selection([
        #    ('S','Yes, have a pension'),
        #    ('N','No, don\'t have a pension'),
        #     ],    'Pension worker', select=True,),
        'type':fields.selection([
            ('0','Activo (No Pensionado)'),
            ('1','Pensionado y cotiza'),
            ('2','Pensionado y no cotiza'),
            ('3','Activo > 65 años (nunca pensionado)'),
             ],    'Type worker', select=True,),
        #'apv_ids':fields.one2many('hr.apv', 'employee_id', 'APV added', required=False),
        'pension_vol_disc_ids':fields.one2many('hr.pension.vol.discount', 'employee_id', 'Pension voluntary discount added', required=False),
        'family_responsibilities_ids':fields.one2many('hr.family.responsibilities', 'employee_id', 'Family responsibilities', required=False),
        'ccaf_credits_ids':fields.one2many('hr.ccaf.credits', 'employee_id', 'CCAF credits', required=False,),
        'insurance_ids':fields.one2many('hr.insurance', 'employee_id', 'Insurance added', required=False),
        'pants_size':fields.char('Pants size', size=64, required=False, readonly=False),
        'shirt_size':fields.char('Shirt size', size=64, required=False, readonly=False),
        'shoe_size':fields.char('Shoe size', size=64, required=False, readonly=False),
    }
    
    
   
hr_employee()



class res_users(osv.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    
    def create(self, cr, uid, data, context=None):
        name = data.get('name', False)
        lname = name.split(' ')
        login = lname[0][0]+lname[1] if lname.__len__()>0 else lname[0] or False
        
        if not data.get('login', False):
            if login:
                login = {'login':login.lower()}
                data.update(login)
                
        return super(res_users,self).create(cr, uid, data, context)    
    
    

res_users()

class hr_job(osv.osv):
    #_name = 'hr.job'
    _inherit = 'hr.job' 
    _columns = {
        'heavy_duty':fields.boolean('Heavy duty'),
        'heavy_duty_quote':fields.float('Heavy duty quote'),
        
    }
hr_job()


