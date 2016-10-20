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

{
        "name" : "Chilean Payroll",
        "version" : "3",
        "author" : "Pedro Arroyo <parroyo@mallconnection.com>",
        "website" : "www.mallconnection.cl",
        'category': 'Localization',
        "description": """  """,
        "depends" : [
                     'base',
                     'hr',
                     'account',
                    
                     ],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "data" : [
            "security/ir.model.access.csv",
            "security/hr_security.xml",
            "data/hr_payroll_data.xml",
        ],
        "update_xml" : [
                        'xml/hr_afc_view.xml',
                        'xml/hr_apv_view.xml',
#                        'hr_bonus_view.xml',
#                        'hr_bonus_type_view.xml',
                        'xml/hr_ccaf_institutions_view.xml',
                        'xml/hr_ccaf_credits_view.xml',
                        'xml/hr_constants_view.xml',
                        'xml/hr_contract_view.xml',
                        'xml/hr_employee_view.xml', 
                        'xml/hr_family_assignment_view.xml',
                        'xml/hr_family_responsibilities_view.xml',
                        'xml/hr_fixed_allocation_view.xml',
                        'xml/hr_health_institutions_view.xml',
                        'xml/hr_insurance_view.xml',
                        'xml/hr_payslip_run_view.xml',
                        'xml/hr_payslip_view.xml',
                        'xml/hr_pension_indicators_view.xml',
                        'xml/hr_pension_scheme_view.xml',
                        'xml/hr_pension_vol_discount_view.xml',
                        'xml/hr_security_institutions_view.xml',
                        'xml/hr_single_tax_constant_view.xml',
                        'xml/hr_single_tax_view.xml',
                        'xml/res_company_view.xml',
                        'xml/hr_report.xml',
                        'xml/resource_view.xml',
                        'wizard/hr_master_payroll_report_view.xml',
                        ],# 'security/ir.model.access.csv'],
        #"qweb": ["static/src/xml/widget_radio.xml"],
        "installable": True
}
