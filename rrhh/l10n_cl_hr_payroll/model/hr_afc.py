#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Pedro Arroyo <parroyo@mallconnection.com>
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

class hr_afc(osv.osv):
    _name = 'hr.afc'
    _columns = {
            'name': fields.char('Description'), 
            'hr_contract_type_id': fields.many2one('hr.contract.type', string='Contract type'),
            'employer_charge': fields.float('employer charge (%)', size=6, required=True),
            'employee_charge': fields.float('employee charge (%)', size=6, required=True),
            'hr_constants_id':fields.many2one('hr.constants', 'Constant', required=False), 
    
    }
    