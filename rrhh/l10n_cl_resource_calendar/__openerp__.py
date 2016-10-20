# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Pedro Arroyo <parroyo@mallconnection.com>,
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name" : "Resource calendar holidays",
    "version" : "1.1",
    "author" : "Pedro Arroyo<parroyo@mallconnection.com>",
    "website" : "www.mallconnection.cl",
    "category" : "base",
    "description": """
    This module implements the structure to administer legal holidays. Designed to Chilean law.
    
    """,
    "depends" : ['resource','hr_payroll'],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [
                    'views/resource_calendar_holiday_view.xml',
                    'views/hr_worked_days_view.xml',
                    ],
    "data" : [
        "security/ir.model.access.csv",
        ],
    "installable": True
}

