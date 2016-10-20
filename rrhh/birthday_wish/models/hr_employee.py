# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Medma - http://www.medma.net
#    All Rights Reserved.
#    Medma Infomatix (info@medma.net)
#
#    Coded by: Turkesh Patel (turkesh.patel@medma.in)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, orm, fields
#from openerp.addons.base.ir.ir_qweb import HTMLSafe
from datetime import datetime, timedelta, time, date
from openerp.tools.translate import _

class hr_employee(osv.osv):
    _name = 'hr.employee' 
    _inherit = ['hr.employee', 'mail.thread', 'ir.needaction_mixin']

    def get_birthdate(self, cr, uid, ids, fields, arg, context):

        x={}
        today = date.today()
        for record in self.browse(cr, uid, ids):
            if record.birthday:
                born = datetime.strptime(record.birthday,"%Y-%m-%d")

                try: 
                    birthday = born.replace(year=today.year)
                except ValueError: # raised when birth date is February 29 and the current year is not a leap year
                    birthday = born.replace(year=today.year, month=born.month+1, day=1)

                x[record.id]= birthday.strftime("%Y-%m-%d")
    
        return x 
    def get_years(self, cr, uid, ids, fields, arg, context):

        x={}
        today = date.today()
        
        for record in self.browse(cr, uid, ids):
        
            if record.birthday:
                born = datetime.strptime(record.birthday,"%Y-%m-%d")
                x[record.id]= today.year - born.year - ((today.month, today.day) < (born.month, born.day))                        
    
        return x 

    _columns = {
        'birth_date': fields.function(get_birthdate, method=True, type='date', string='Birth date', store=True, readonly=True),
        'years_old':  fields.function(get_years, method=True, type='integer', string='Years old', store=True, readonly=True),
    }

    def send_birthday_email(self, cr, uid, ids=None, context=None):
        if not context: context = {}
        employee_obj = self.pool.get('hr.employee')
        celebrate=[]
        dist_list_email=""
        temp_obj = self.pool.get('email.template')
        group_obj = self.pool.get('mail.group')
        wish_template_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'birthday_wish', 'email_template_birthday_wish')[1]
        wish_all_com_template_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'birthday_wish', 'email_template_birthday_wish_all_company')[1]
        group_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'birthday_wish', 'group_birthday')[1]
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        employee_ids = employee_obj.search(cr, uid, [('birth_date', 'like', today_month_day)])
        if employee_ids:
            for employee_id in employee_obj.browse(cr, uid, employee_ids,context=context):
                if employee_id.work_email:
                    temp_obj.send_mail(cr, uid, employee_id.company_id.birthday_mail_template and employee_id.company_id.birthday_mail_template.id or wish_template_id,
                                   employee_id.id, force_send=True, context=context)
                group_obj.message_post(cr, uid, group_id, body=_('Happy Birthday Dear %s.') % (employee_id.name), partner_ids=[employee_id.id], context=context)
                #aviso de feliz cumples a todo el grupo
                self.message_post(cr, uid, employee_id.id, body=_('Happy Birthday.'), employee_ids=[employee_id.id], context=context)
                celebrate.append(employee_id.name)
                dist_list_email = employee_id.company_id.dist_list_email
                
            context.update({'celebrate':celebrate})
            context.update({'dist_list_email': dist_list_email})
            
            temp_obj.send_mail(cr, uid, wish_all_com_template_id, employee_ids[0], force_send=True, context=context)
        return None

hr_employee()