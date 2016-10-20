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


class res_company(osv.osv):
    _name="res.company"
    _inherit ="res.company"
    _columns={
              'mutual_id': fields.many2one("hr.health.institutions", "Mutual institutions", domain="[('mutual_org','=',True)]"),
              'ccaf_id': fields.many2one("hr.ccaf.institutions", "CCAF institutions"),
              'mutual_quote': fields.float('Mutual quote'),
              'ccaf_quote': fields.float('CCAF quote'),
              }
res_company()