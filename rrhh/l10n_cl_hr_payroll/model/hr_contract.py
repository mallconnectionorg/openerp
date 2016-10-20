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

#class hr_contract_type(osv.osv):
#    #_name = 'hr.contract.type'
#    _inherit = 'hr.contract.type' 
#    _columns = {
#        'hr_afc_ids':fields.one2many('hr.afc', 'hr_contract_type_id', 'AFC', required=False),
#    }
#hr_contract_type()

class hr_contract(osv.osv):
    
    def _get_invoices(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
            
        obj_contract = self.browse(cr, uid, ids,context)[0]
        
        if not obj_contract.employee_id.address_home_id and obj_contract.employee_id:
            return result
            
        invoice_ids = self.pool.get('account.invoice').search(cr,uid,[('partner_id','=',obj_contract.employee_id.address_home_id.id),('state','=','open')])
        for i in invoice_ids:
            result[ids[0]].append(i)
             
        return result
    
    
    
    _name="hr.contract"
    _inherit ="hr.contract"
    _columns={
              'collation': fields.integer("Collation", size=6,),
              'mobilization': fields.integer("Mobilization", size=6,),
              'company_id': fields.many2one('res.company', 'Company', ),
              'legal_gratification':fields.selection([
                  ('assessment_system','Repartir el 30% de la utilidad líquida entre todos los trabajadores, en proporción a las remuneraciones percibidas por cada uno de ellos.'),
                  ('25_payment_system','Pagar o abonar al trabajador el 25% de las remuneraciones devengadas durante el año, cualquiera sea la utilidad líquida que obtenga la empresa. Esta gratificación tiene un tope equivalente a 4,75 ingresos mínimos mensuales.'),
                   ('grat_fixed', 'Gratification fixed')
                   ],    'Legal gratification'),
              'min_taxable':fields.boolean('Minimum taxable',help='Calculate minimum taxable as wage base ', required=False), 
              'gratification_fixed': fields.float('Gratification fixed' ),
              'fixed_allocations_ids':fields.one2many('hr.fixed.allocation', 'contract_id', 'Fixed allocations', required=False),
              #'bonus_ids':fields.one2many('hr.bonus', 'contract_id', 'Bonuses', required=False),
              #'bonus_ids':fields.many2many('hr.bonus', 'bonus_contract_rel', 'contract_id', 'bonus_id', 'Bonuses'), 
              'invoice_ids':fields.function(_get_invoices, method=True, type='one2many', relation='account.invoice', string='Pending invoices be paid'),
              'extra_hour_factor':fields.float('Extra hour factor', digits=[2,8]),
              'biweekly_agreed': fields.float('Biweekly agreed'),
              'young_worker_grant':fields.boolean('Young Worker Grant'),
              'hours': fields.integer('hours') 
              }
    _defaults = {  
        'extra_hour_factor': 0.00777770,  
        }
    
    def __init__(self, pool, cr):
        """Add a new state value"""
        if not 'daily' in dict(super(hr_contract, self)._columns['schedule_pay'].selection):
            super(hr_contract, self)._columns['schedule_pay'].selection.append(('daily', 'Daily'))
            
        return super(hr_contract, self).__init__(pool, cr)
    
    def action_get_min_taxable(self, cr, uid,ids, min_tax, context=None):
        res = {'value': {}}
        if min_tax:
            constant_ids = self.pool.get("hr.constants").search(cr, uid,[('state','=','active')])
            constant_min_tax = self.pool.get("hr.constants").read(cr,uid,constant_ids,['rmi_employee_in_dependent'])[0]
            
            res['value']['wage'] = constant_min_tax['rmi_employee_in_dependent']
        return res
hr_contract()

class hr_contract_type(osv.osv):
    #_name = 'hr.contract.type'
    _inherit = 'hr.contract.type' 
    _columns = {
        'hr_afc_ids':fields.one2many('hr.afc', 'hr_contract_type_id', 'AFC', required=False),
    }
hr_contract_type()

