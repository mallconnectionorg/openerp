# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Pedro Arroyo M (http://esteban52.wordpress.com)
#                            Potenciado por Mallconnection S.A. (www.mallconnection.com)
#                            contactame mail:        parroyo@mallconnection.com;esteban.arroyo@gmail.com;esteban_52@hotmail.com
#                                                    Twitter:        @PedroArroyoM
#                                                    linkedin:    https://cl.linkedin.com/pub/pedro-arroyo/25/a64/602
#    
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


from osv import osv
from osv import fields

class resource_calendar_holiday(osv.osv):
    '''
    Open ERP Model
    '''
    _name = 'resource.calendar.holiday'
    _description = 'resource.calendar.holiday'
 
    _columns = {
            'name':fields.char('Name', size=64, required=False, readonly=False),
            'date': fields.date('Date'), 
            'type':fields.selection([
                ('civil','Civil'),
                ('Religious','Religious'),
                 ],    'Type', select=True),
            'irrevocable':fields.selection([
                ('first_category','First category'),
                ('second_category','Second category'),
                ('third_category','Third category'),
                 ],    'Irrevocable', select=True),
            #'commune':fields.boolean('Only in the communes', required=False), 
            #'commune_ids':fields.one2many('OpenerpModel', 'partner_category_rel', 'model1_id', 'model2_id', 'Label'), 
            #'region':fields.boolean('Only in the regions', required=False), 
            #'region_ids':fields.one2many('OpenerpModel', 'partner_category_rel', 'model1_id', 'model2_id', 'Label'), 
            
            
        }
    
    
    
resource_calendar_holiday()


class resource_calendar(osv.osv):
    _inherit = "resource.calendar"
    
    def working_hours_on_day(self, cr, uid, resource_calendar_id, day, context=None):
        """Calculates the  Working Total Hours based on Resource Calendar and
        given working day (datetime object). if day is public holiday and employee have schedule work rotative is working hours.

        @param resource_calendar_id: resource.calendar browse record
        @param day: datetime object

        @return: returns the working hours (as float) men should work on the given day if is in the attendance_ids of the resource_calendar_id (i.e if that day is a working day), returns 0.0 otherwise
        """
        res = 0.0
        p_holidays_obj = self.pool.get('resource.calendar.holiday')
        p_holidays_ids = p_holidays_obj.search(cr,uid,[])
        p_holidays = p_holidays_obj.read(cr,uid,p_holidays_ids,['date'],context=context)
        
        for working_day in resource_calendar_id.attendance_ids:
            if (int(working_day.dayofweek) + 1) == day.isoweekday() and day not in [item['date'] for item in p_holidays]:
                res += working_day.hour_to - working_day.hour_from
        return res
        

resource_calendar()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: