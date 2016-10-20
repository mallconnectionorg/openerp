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
import time, datetime
import calendar
from dateutil.relativedelta import relativedelta
import openerp.exceptions

class hr_pension_indicators(osv.osv):
    
    _name = 'hr.pension.indicators'
    
    def _get_lines_hr_afc(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
        cr.execute('''
        select ha.id from hr_afc ha inner join hr_constants hc on  hc.id = ha.hr_constants_id where hc.state = \'active\' 
        ''')
        res = cr.fetchall()
        for r in res:
            result[ids[0]].append(r[0])
        return result    

    def _get_lines_family_assignment(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
        cr.execute('''
        select hf.id from hr_family_assignment hf inner join hr_constants hc on  hc.id = hf.hr_constants_id where hc.state = 'active'
        ''')
        res = cr.fetchall()
        for r in res:
            result[ids[0]].append(r[0])
        return result   

    _columns = {

        'name':fields.char('Descripcion', size=64, required=False, readonly=True), 
        'from':fields.date('From',required=True),
        'to':fields.date('To',required=True),
        #'state':fields.selection([('active','Active'),('inactive', 'Inactive')], 'State'),
        'uf':fields.float('UF value', readonly=True), 
        'utm':fields.float('UTM value', readonly=True), 
        'uta':fields.float('UTA value', readonly=True),
        'health_percent': fields.float('Health %', readonly=True),
        'sis': fields.float('SIS %', readonly=True),
        'isl':fields.float('ISL %', readonly=True),
        'security_percent': fields.float('Security %', readonly=True),
        'Annual_cap_on_agreed_deposit': fields.float('Annual cap on agreed deposit', readonly=True), #deposito_convenido_tope_anual
        'apv_monthly_limit':fields.float('APV monthly limit', readonly=True), #APV tope mensual 
        'apv_Annual_limit':fields.float('APV Annual limit', readonly=True),
        'rmi_employee_in_dependent': fields.float('Dependent and Independent Workers ($)', readonly=True,), #Trab. Dependientes e Independientes
        'rmi_employee_under18_over65': fields.float('Under 18 and over 65 ($)', readonly=True,), #Menores de 18 y Mayores de 65
        'rmi_private_house_workers': fields.float('Workers in private homes ($)', readonly=True,), #trabajador casa particular
        'rti_afp_added' : fields.float('For members of an AFP (UF)', readonly=True,),#Para afiliados a una AFP
        'rti_ips_added' : fields.float('For members of the IPS (former INP)', readonly=True,), #Para afiliados al IPS
        'rti_security_unemployee' : fields.float('For Unemployment Insurance', readonly=True,), #Para Seguro de Cesantía 
        'hr_afc_detail_ids':fields.function(_get_lines_hr_afc, method=True, type='one2many', relation='hr.afc', string='Unemployment Insurance (AFC)'),#fields.one2many('hr.afc', 'hr_constants_id', 'Unemployment Insurance (AFC)', readonly=False),
        'hr_family_assignment_ids':fields.function(_get_lines_family_assignment, method=True, type='one2many', relation='hr.family.assignment', string='Family Assignment'),#fields.one2many('hr.family.assignment', 'hr_constants_id', 'Family Assignment', readonly=False),
        'hr_single_tax_ids':fields.one2many('hr.single.tax', 'hr_pension_indicators_ids', 'Single tax', required=False),
                } 
    
    def action_compute_indicators(self, cr, uid, ids, context=None):
        
        res=0
        
        obj_pension_indicators = self.browse(cr, uid, ids, context)[0] if self.browse(cr, uid, ids, context).__len__()>0 else None
        
        if obj_pension_indicators == None:
            return
        
        obj_currency = self.pool.get('res.currency')
        
        obj_constants = self.pool.get('hr.constants').search(cr, uid, [('state','=','active')], context=context)
        obj_constants = self.pool.get('hr.constants').browse(cr, uid, obj_constants, context) #obj_constants[0] if obj_constants.__len__()>0 else None
        obj_constants = obj_constants[0]
        obj_clp = self.pool.get('res.currency').search(cr, uid, [('name','=','CLP')], context=context)
        obj_clp = self.pool.get('res.currency').browse(cr, uid, obj_clp, context=context)
        obj_clp = obj_clp[0]
        obj_uf = obj_constants.uf
        obj_utm = obj_constants.utm
        if not obj_uf or not obj_utm:
                raise openerp.exceptions.Warning('No esta definida una moneda para UF o para UTM en la hoja de constantes vigente')
            
        
        obj_single_tax_constants = obj_constants.hr_single_tax_constant_ids
        obj_single_tax = self.pool.get('hr.single.tax')
        
        cnx = {'date': obj_pension_indicators.to or time.strftime('%Y-%m-%d')}
        
        indicators={}
        indicators['name']="Indicadores previsionales, UF al %s" % obj_pension_indicators.to
        indicators['uf']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, 1,False,False,False, cnx)
        indicators['utm']=obj_currency.compute(cr, uid, obj_utm.id, obj_clp.id, 1,False,False,False, cnx)
        indicators['uta']=obj_currency.compute(cr, uid, obj_utm.id, obj_clp.id, 12,False,False,False, cnx)
        indicators['health_percent']=obj_constants.health_percent
        indicators['isl']=obj_constants.isl
        indicators['sis']=obj_constants.sis
        indicators['security_percent']=obj_constants.security_percent
        indicators['Annual_cap_on_agreed_deposit']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, obj_constants.Annual_cap_on_agreed_deposit,True,False,False, cnx)
        indicators['apv_monthly_limit']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, obj_constants.apv_monthly_limit,True,False,False, cnx)
        indicators['apv_Annual_limit']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, obj_constants.apv_Annual_limit,True,False,False, cnx)
        indicators['rmi_employee_in_dependent']=obj_constants.rmi_employee_in_dependent
        indicators['rmi_employee_under18_over65']=obj_constants.rmi_employee_under18_over65
        indicators['rmi_private_house_workers']=obj_constants.rmi_private_house_workers
        indicators['rti_afp_added']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, obj_constants.rti_afp_added,True,False,False, cnx)
        indicators['rti_ips_added']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, obj_constants.rti_ips_added,True,False,False, cnx)
        indicators['rti_security_unemployee']=obj_currency.compute(cr, uid, obj_uf.id, obj_clp.id, obj_constants.rti_security_unemployee,True,False,False, cnx)
        
        #self.write(cr,uid,ids,indicators)
        single_tax_lines=[]
        
        #dt = datetime.datetime.strptime(obj_pension_indicators.to, "%Y-%m-%d")
        #dt = dt + relativedelta(months=-1)
        #dt = dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])
        #cnx = {'date': dt.strftime('%Y-%m-%d') or time.strftime('%Y-%m-%d')}
        
        #single_tax_ids = obj_single_tax.search(cr,uid, [('hr_pension_indicators_ids','=','active')], context=context)
        if obj_pension_indicators.hr_single_tax_ids.__len__()>0:
            obj_single_tax.unlink(cr,uid,[single_tax.id for single_tax in obj_pension_indicators.hr_single_tax_ids],context)
        i = 0    
        for item in dict(obj_single_tax._columns['period'].selection):
            div = 0.0
            if item=='monthly':
                div = 1
            elif item=='bi-weekly':
                div = 2
            elif item=='daily':
                div = 30
            elif item=='weekly':  
                div = 4.285712722              
            
            
            for single_tax_constant in obj_single_tax_constants:
                single_tax_line={}
                single_tax_line['period']= item
                single_tax_line['from_'] = obj_currency.compute(cr, uid, obj_utm.id, obj_clp.id, single_tax_constant.from_/div,True,False,False, cnx)
                single_tax_line['to_'] = obj_currency.compute(cr, uid, obj_utm.id, obj_clp.id, single_tax_constant.to_/div,True,False,False, cnx)
                single_tax_line['percent'] = single_tax_constant.percent
                single_tax_line['reduction'] = obj_currency.compute(cr, uid, obj_utm.id, obj_clp.id, single_tax_constant.reduction/div,False,False,False, cnx)
                #single_tax_line['hr_pension_indicators_ids'] = ids[0]
                single_tax_lines.append([0,0,single_tax_line])
                
        indicators['hr_single_tax_ids']=single_tax_lines
        #obj_single_tax.write(cr,uid,ids,single_tax_lines)
        self.write(cr,uid,ids,indicators)
        return res
    
    
    
hr_pension_indicators()