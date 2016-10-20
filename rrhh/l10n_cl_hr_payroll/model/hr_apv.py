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

class hr_apv(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'hr.apv'
    _description = 'APV'
 
    _columns = {
            'name':fields.char('Contract number', size=64, required=False, readonly=False),
            'type':fields.selection([
                ('apv','APV'),
                ('apvi','APVI'),
                ('apvc','APVC'),
                 ],    'Type', select=True),
            'employee_id': fields.many2one('hr.employee', string='Employee'),
            'security_institution_id': fields.many2one('hr.security.institutions', string='Security institution'),
            'currency_id':fields.many2one('res.currency', string='Currency', domain="[('name','in',['UF','CLP'])]"),
            'disc_type':fields.selection([
                ('percent','Percent'),
                ('amount','Amount'),
                 ],    'Discount type', select=True),
            'amount': fields.float('Amount', digits_compute=dp.get_precision('APV amount')),
            'amount_agreed_deposit': fields.float('Amount agreed deposit', digits_compute=dp.get_precision('APV amount')),
            'state':fields.selection([
                ('draft','Draft'),
                ('done','Done'),
                 ],    'State', select=True, readonly=True),
            'type_payment':fields.selection([
                ('1','Direct'),
                ('2','Indirect'),
                 ],    'Type payment', select=True, readonly=False),
            'code':fields.char('Code', size=64, required=False, readonly=False),
            
            
        }
    
    
hr_apv()