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

class hr_fixed_allocation(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.fixed.allocation'
    _description = 'hr.fixed.allocation'
 
    _columns = {
            'name':fields.char('Description', size=64, required=True, readonly=False),
            #'code':fields.char('Code', size=64, required=False, readonly=False),
            #'type':fields.selection([
            #    ('collation','Collation'),
            #    ('mobilization','Mobilization'),
            #    ('cash_loss','Cash loss'),
            #    ('tool_wear','Tool wear')
            #    ('bonification','Bonification')
            #     ],    'Type'),
            'amount': fields.float('Amount', digits=(3,2),required=True),
            'allocation_type_id':fields.many2one('hr.fixed.allocation.type', 'Allocation type', required=True), 
            'contract_id':fields.many2one('hr.contract', 'Contract', required=False), 
            #'taxable':fields.boolean('Taxable', required=False), 
            
        }
hr_fixed_allocation()
class hr_fixed_allocation_type(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.fixed.allocation.type'
    _description = 'hr.fixed.allocation type'
 
    _columns = {
            'name':fields.char('Description', size=64, required=True, readonly=False),
            'code':fields.char('Code', size=64, required=False, readonly=False),
            'type':fields.selection([
                ('collation','Collation'),
                ('mobilization','Mobilization'),
                ('cash_loss','Cash loss'),
                ('tool_wear','Tool wear'),
                ('bonification','Bonification')
                 ],    'Type'),
            'taxable':fields.boolean('Taxable', required=False), 
            
        }
hr_fixed_allocation_type()