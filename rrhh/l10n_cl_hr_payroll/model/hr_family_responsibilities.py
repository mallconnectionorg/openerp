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

class hr_family_responsibilities(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.family.responsibilities'
    _description = 'openerpmodel'
 
    _columns = {
            'name':fields.char('Name', size=64, required=True, readonly=False),
            'type':fields.selection([
                ('simple','simple responsibility'),
                ('maternal','maternal responsibility'),
                ('invalid','invalid responsibility'),
                 ],    'State', select=True),
            'relationship':fields.selection([
                ('father','father'),
                ('son','son / daughter'),
                ('spouse','spouse'),
                ('Father in law','Father in law / mother in law'),
                ('son','son / daughter'),
                ('second','second'),
                ('Grandfather','Grandfather / Grandmother'),
                ('grandchild','grandchild / granddaughter'),
                ('sister','sister / brother'),
                ('brother in law','brother in law / sister in law'),
                 ],    'Relationship', select=True, readonly=False),
            'vat': fields.char('TIN', size=32, help="Tax Identification Number. Check the box if this contact is subjected to taxes. Used by the some of the legal statements."),
            'employee_id': fields.many2one('hr.employee', string='Employee'),
            
        }
hr_family_responsibilities()