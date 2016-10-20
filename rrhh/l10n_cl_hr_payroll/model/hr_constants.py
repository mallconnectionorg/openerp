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
from openerp.tools.translate import _

class hr_constants(osv.osv):

    _name = 'hr.constants'
    _columns = {
        'name': fields.char('Nombre'), 
        'state':fields.selection([('active','Active'),('inactive', 'Inactive')], 'State'),
        'health_percent': fields.float('Health %', required=True),
        'sis': fields.float('SIS %', required=True),
        'isl':fields.float('ISL %', required=True),
        'uf':fields.many2one('res.currency', 'UF', required=False,domain="[('name','=','UF')]"), 
        'utm':fields.many2one('res.currency', 'UTM', required=False,domain="[('name','=','UTM')]"), 
        'security_percent': fields.float('Security %', required=True),
        'Annual_cap_on_agreed_deposit': fields.float('Annual cap on agreed deposit (UF)', required=True), #deposito_convenido_tope_anual
        'apv_monthly_limit': fields.float('APV monthly limit (UF)', required=True), #APV tope mensual 
        'apv_Annual_limit': fields.float('APV Annual limit (UF)', required=True),
        'rmi_employee_in_dependent': fields.float('Dependent and Independent Workers ($)', size=6, required=True,), #Trab. Dependientes e Independientes
        'rmi_employee_under18_over65': fields.float('Under 18 and over 65 ($)', size=6, required=True,), #Menores de 18 y Mayores de 65
        'rmi_private_house_workers': fields.float('Workers in private homes ($)', size=6, required=True,), #trabajador casa particular
        'rti_afp_added' : fields.float('For members of an AFP (UF)', size=6, required=True,),#Para afiliados a una AFP
        'rti_ips_added' : fields.float('For members of the IPS (former INP) (UF)', size=6, required=True,), #Para afiliados al IPS
        'rti_security_unemployee' : fields.float('For Unemployment Insurance (UF)', size=6, required=True,), #Para Seguro de Cesantía 
        'hr_afc_detail_ids':fields.one2many('hr.afc', 'hr_constants_id', 'Unemployment Insurance (AFC)', required=False),
        'hr_family_assignment_ids':fields.one2many('hr.family.assignment', 'hr_constants_id', 'Family Assignment', required=False),
        'hr_single_tax_constant_ids':fields.one2many('hr.single.tax.constant', 'hr_constants_id', 'Single tax', required=False),
    }
    _defaults = {  
        'state': 'active',  
        }
    
    def create(self, cr, uid, vals, context=None):
        cr.execute("update hr_constants set state='inactive';")
        return super(hr_constants, self).create(cr, uid, vals, context=context)
   
hr_constants()
