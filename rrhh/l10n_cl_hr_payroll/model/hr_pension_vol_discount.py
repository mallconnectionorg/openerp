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
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from mock import DEFAULT

class hr_pension_vol_discount(osv.osv):
    '''
    Pension discount volunteer for apv, apvc and voluntary saving
    '''
    _name = 'hr.pension.vol.discount'
    _description = 'Pension discount volunteer'
 
    _columns = {
            'name':fields.char('Name', size=64, required=True, readonly=False),
            'contract_number':fields.char('Contract number', size=20, required=True, readonly=False),
            'description':fields.char('Description', size=64, required=False, readonly=False),
            'type':fields.selection([
                                    ('apvi','APVI'),
                                    ('apvc','APVC'),
                                    ('count2','Count 2'),
                                    ('agreed_deposit','Agreed deposit'),
                                     ],    'Type', select=True, required=True),
            'employee_id': fields.many2one('hr.employee', string='Employee'),
            'security_institution_id': fields.many2one('hr.security.institutions', required=True, string='Security institution'),
            'currency_id':fields.many2one('res.currency', string='Currency', required=True, domain="[('name','in',['UF','CLP'])]"),
            'disc_type':fields.selection([
                                            ('percent','Percent'),
                                            ('amount','Amount'),
                                             ],    'Discount type', required=True, select=True),
            'amount': fields.float('Amount', digits_compute=dp.get_precision('APV amount')),
            'state':fields.selection([
                                        ('draft','Draft'),
                                        ('confirmed','Confirmed'),
                                        ('cancelled','Cancelled')
                                         ],    'State', select=True, readonly=True),
            'type_payment':fields.selection([
                                            ('1','Direct'),
                                            ('2','Indirect'),
                                             ],    'Type payment', select=True),
            'code':fields.char('Code', size=64, required=False, readonly=False),
            
            

        }
    _defaults = {  
        'state': 'draft',  
        }
    _sql_constraints = [
                            (
                                'contract_employee_unique',
                                'unique (contract_number, employee_id)',
                                _('Contract number must be unique per employee !')
                            )
                        ]
    
    def signal_draft(self,cr,uid,ids,context=None):
        return self.write(cr, uid, ids, {'state':'draft'}, context)
    
    def signal_confirm(self,cr,uid,ids,context=None):
        return self.write(cr, uid, ids, {'state':'confirmed'}, context)

    def signal_cancel(self,cr,uid,ids,context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context)
       
        
hr_pension_vol_discount()