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

class resource_calendar(osv.osv):
    '''
    Open ERP Model
    '''
    _inherit = "resource.calendar"
    _description = 'openerpmodel'
 
    _columns = {
            'attendance_ids' : fields.one2many('resource.calendar.attendance', 'calendar_id', 'Working Time'),
            'var_attendance':fields.boolean('Variable working Time', required=False), 
            'var_attendance_ids' : fields.one2many('resource.calendar.variable.attendance', 'calendar_id', 'Variable Working Time'),
        }
resource_calendar()

class resource_calendar_variable_attendance(osv.osv):
    _name = "resource.calendar.variable.attendance"
    _description = "Resource Calendar"
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'dayofweek': fields.selection([('0','Monday'),('1','Tuesday'),('2','Wednesday'),('3','Thursday'),('4','Friday'),('5','Saturday'),('6','Sunday')], 'Day of Week', required=True, select=True),
        'date_from' : fields.date('Starting Date'),
        'hour_from' : fields.float('Work from', required=True, help="Start and End time of working.", select=True),
        'hour_to' : fields.float("Work to", required=True),
        'calendar_id' : fields.many2one("resource.calendar", "Resource's Calendar", required=True),
    }
    _order = 'date_from, dayofweek, hour_from'

    _defaults = {
        'dayofweek' : '0'
    }
resource_calendar_variable_attendance()