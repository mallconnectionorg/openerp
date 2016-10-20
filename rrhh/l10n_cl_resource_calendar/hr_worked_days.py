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
from datetime import *
from openerp.tools.translate import _


class hr_worked_days(osv.osv):
    _name = 'hr.worked.days'
    _description = 'hr.worked.days'
    
    
    
    def _totals_calc(self, cr, uid, ids, field_name, arg, context=None):

        this = self.browse(cr,uid,ids)[0]
        holidays_ids = self.pool.get('resource.calendar.holiday').search(cr,uid,[]) if self.pool.get('resource.calendar.holiday') else None
        holydays_obj = self.pool.get('resource.calendar.holiday').browse(cr,uid,holidays_ids) if holidays_ids else None
        if holydays_obj: holydays_date = [i.date for i in holydays_obj]
        
        res={}
        wdays = 0
        whours = 0
        wovertime = 0
        wsunday = 0
        whsunday = 0
        woversunday = 0
        holidays = 0
        holidays_hours = 0
        holidays_otime = 0
        
        try:
            for wdline in this.worked_days_line_ids:

                if datetime.strptime(wdline.name,'%Y-%m-%d').isoweekday()==7:
                    wsunday+=1
                    whsunday+=wdline.worked_hours
                    woversunday+=wdline.overtime
                else:
                    wdays += 1
                    whours +=  wdline.worked_hours
                    wovertime += wdline.overtime
                    
                if wdline.name in holydays_date:
                    holidays += 1
                    holidays_hours = wdline.worked_hours
                    holidays_otime = wdline.overtime
                 
            res[this.id] = {
                    'total_worked_days': wdays,
                    'total_worked_hours': whours,
                    'total_overtime':wovertime,
                    'total_worked_sunday_days': wsunday,
                    'total_worked_sunday_hours': whsunday,
                    'total_worked_sunday_overtime': woversunday,
                    'total_worked_holyday_days': holidays,
                    'total_worked_holyday_hours':holidays_hours,
                    'total_worked_holyday_overtime':holidays_otime,
                                    }
        except:
            pass
        return res
    
    _columns = {
            'name':fields.char('Name', size=64, required=True),
            'month': fields.selection([
                    ('january','January'),
                    ('february','February'),
                    ('march','March'),
                    ('april','April'),
                    ('may','May'),
                    ('june','June'),
                    ('july','July'),
                    ('august','August'),
                    ('september','September'),
                    ('october','October'),
                    ('november','November'),
                    ('december','December'),
                 ],    'Month', select=True,),
            'year': fields.integer('Number of year', required=True),
            'contract_id':fields.many2one('hr.contract', 'Contract', required=True),
            'worked_days_line_ids':fields.one2many('hr.worked.days.line', 'worked_days_id', 'Days no work', required=False),  
            'total_worked_days': fields.function(_totals_calc, type='integer', string='Total worked days', store=False, multi='other_info'),
            'total_worked_hours': fields.function(_totals_calc, type='integer', string='Total worked hours', store=False, multi='other_info'),
            'total_overtime': fields.function(_totals_calc, type='integer', string='Total worked overtime', store=False, multi='other_info'),
            'total_worked_sunday_days': fields.function(_totals_calc, type='integer', string='Total sunday worked', store=False, multi='other_info'),
            'total_worked_sunday_hours': fields.function(_totals_calc, type='integer', string='Total sunday hours worked', store=False, multi='other_info'),
            'total_worked_sunday_overtime': fields.function(_totals_calc, type='integer', string='Total sunday overtime', store=False, multi='other_info'),
            'total_worked_holyday_days': fields.function(_totals_calc, type='integer', string='Total worked holiday', store=False, multi='other_info'),
            'total_worked_holyday_hours': fields.function(_totals_calc, type='integer', string='Total worked hours holiday', store=False, multi='other_info'),
            'total_worked_holyday_overtime': fields.function(_totals_calc, type='integer', string='Total worked overtime holiday', store=False, multi='other_info'),
            
        }
    
hr_worked_days()

class hr_worked_days_line(osv.osv):
    _name = 'hr.worked.days.line' 
    _columns = {
            #TODO : import time required to get currect date
            'name': fields.date('worked date',required=True),
            'worked_hours': fields.float('Worked hours',required=True),
            'overtime': fields.float('Overtime',required=True),
            'note': fields.text('Description'),
            'worked_days_id':fields.many2one('hr.worked.days', 'head', required=False), 
                    }
    
hr_worked_days_line()

class hr_payslip(osv.osv):

    _inherit = 'hr.payslip'
    
    
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = super(hr_payslip,self).get_worked_day_lines(cr, uid, contract_ids, date_from,date_to, context)
        months = [
                    'january',
                    'february',
                    'march',
                    'april',
                    'may',
                    'june',
                    'july',
                    'august',
                    'september',
                    'october',
                    'november',
                    'december',
                  
                  ]
        month_name = months[datetime.strptime(date_from,'%Y-%m-%d').month-1]
        
        contract_obj = self.pool.get('hr.contract').browse(cr, uid, contract_ids)[0]
        workdays_ids = self.pool.get('hr.worked.days').search(cr, uid, [('contract_id','=',contract_ids),('month','=',month_name)])
        if len(workdays_ids)>0:
            workdays_obj = self.pool.get('hr.worked.days').browse(cr, uid, workdays_ids)[0]
            total_worked_days = workdays_obj.total_worked_days
            total_worked_hours = workdays_obj.total_worked_hours
            total_overtime = workdays_obj.total_overtime
            total_worked_sunday_days = workdays_obj.total_worked_sunday_days
            total_worked_sunday_hours = workdays_obj.total_worked_sunday_hours
            total_worked_sunday_overtime = workdays_obj.total_worked_sunday_overtime
            total_worked_holyday_days = workdays_obj.total_worked_holyday_days
            total_worked_holyday_hours = workdays_obj.total_worked_holyday_hours
            total_worked_holyday_overtime = workdays_obj.total_worked_holyday_overtime
            
            if total_worked_days>0 and total_worked_hours>0:
                foo = [i for i in res if i['code']=='WORK100']
                if len(foo)>0:
                    res.remove(foo[0])
                attendances = {
                     'name': _("Normal Working Days paid at 100%"),
                     'sequence': 1,
                     'code': 'WORK100',
                     'number_of_days': total_worked_days,
                     'number_of_hours': total_worked_hours,
                     'contract_id': contract_ids[0],
                }
                res += [attendances]
            
            if total_overtime>0:
                attendances = {
                     'name': _("Overtime"),
                     'sequence': 1,
                     'code': 'OVERTIME',
                     'number_of_days': 0,
                     'number_of_hours': total_overtime,
                     'contract_id': contract_ids[0],
                }            
                res += [attendances]
            
            if total_worked_sunday_days>0 and total_worked_sunday_hours>0:
                attendances = {
                     'name': _("Working in sunday day"),
                     'sequence': 1,
                     'code': 'SUNDAYWORK',
                     'number_of_days': total_worked_sunday_days,
                     'number_of_hours': total_worked_sunday_hours,
                     'contract_id': contract_ids[0],
                }            
                res += [attendances]
            
            if total_worked_sunday_overtime>0:
                attendances = {
                     'name': _("Overtime in sunday day"),
                     'sequence': 1,
                     'code': 'SUNDAYOVERTIME',
                     'number_of_days': 0,
                     'number_of_hours': total_worked_sunday_overtime,
                     'contract_id': contract_ids[0],
                }            
                res += [attendances]
            
            if total_worked_holyday_days>0 and total_worked_holyday_hours>0:
                attendances = {
                     'name': _("Working in Holiday"),
                     'sequence': 1,
                     'code': 'HOLIDAYWORK',
                     'number_of_days': total_worked_holyday_days,
                     'number_of_hours': total_worked_holyday_hours,
                     'contract_id': contract_ids[0],
                }            
                res += [attendances]
            
            if total_worked_holyday_overtime>0:
                attendances = {
                     'name': _("Overtime in Holiday"),
                     'sequence': 1,
                     'code': 'OVERTIMEHOLIDAY',
                     'number_of_days': 0,
                     'number_of_hours': total_worked_holyday_overtime,
                     'contract_id': contract_ids[0],
                }            
                res += [attendances]
        #else:
        #    res = super(hr_payslip,self).get_worked_day_lines(cr, uid, contract_ids, date_from,date_to, context)
        
        return res
        
        
                
hr_payslip()