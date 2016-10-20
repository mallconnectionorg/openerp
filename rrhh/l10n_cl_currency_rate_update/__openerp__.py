#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#   Pedro Arroyo M. <parroyo@mallconnection.com>
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
    "name" : "Chilean Currency Rate Update",
    "version" : "1",
    "author" : "Pedro Arroyo M ; MallConnection",
    "website" : "www.mallconnection.cl",
    "category" : "Financial Management/Configuration",
    "description": """  """,
    "depends" : [
                "base",
                "account", #Added to ensure account security groups are present],
                "currency_rate_update"
                ],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "data" : [
'precision_decimal_data.xml'
    ],
    "update_xml" : [
                    'currency_rate_update_view.xml'
                    ],
    "installable": True
}
