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
from openerp import tools



class hr_security_institutions(osv.osv):
    """Class AFP"""
    _name = 'hr.security.institutions'
    def _total_SIS (self, cr, uid, ids, field_name, arg, context=None):
        if not ids: return()
        res = {}
        obj_constants = self.pool.get('hr.constants').search(cr, uid, [('state','=','active')], context=context)
        obj_constants = self.pool.get('hr.constants').browse(cr, uid, obj_constants, context) 
        obj_constants = obj_constants[0] if obj_constants.__len__()>0 else None
        
        for o in self.browse (cr, uid, ids):
            res[o.id]=0
            if obj_constants!= None:
                res[o.id] = obj_constants.sis
        return res

    def _total_contribution (self, cr, uid, ids, field_name, arg, context=None):
        if not ids: return()
        res = {}
        obj_constants = self.pool.get('hr.constants').search(cr, uid, [('state','=','active')], context=context)
        obj_constants = self.pool.get('hr.constants').browse(cr, uid, obj_constants, context) 
        obj_constants = obj_constants[0] if obj_constants.__len__()>0 else None
        
        for o in self.browse (cr, uid, ids):
            res[o.id]=0
            if obj_constants!= None:
                res[o.id] = obj_constants.security_percent
        return res
    
    def _total_afp (self, cr, uid, ids, field_name, arg, context=None):
        if not ids: return()
        res = {}
        for o in self.browse (cr, uid, ids):
            res[o.id] = o.commission + o.contribution
        return res    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    
    _columns = {
        'name': fields.char('Name', size=50, required=True, translate=True),
        'commission': fields.float('comision', size=6, required=True,),
        'contribution': fields.function(_total_contribution, method=True, type='float', string='Contribution', readonly=True ),#fields.float('contribution', size=6, readonly=True,),
        'SIS': fields.function(_total_SIS, method=True, type='float', string='SIS', readonly=True),#fields.float('SIS', size=6, required=True,),
        'code': fields.char('Previred code', size=3, required=True,),
        'pension_scheme':fields.selection([
           ('AFP','AFP'),
           ('INP','IPS (Ex-INP)'),
           ('SIP','Sin Institución Previsional'),
             ],    'Pension scheme', select=True, readonly=False, ), 
        'eviction_rate': fields.float('Eviction rate', digits=(12,6),),
        #'pension_scheme': fields.many2one('hr.pension.scheme', string='Pension scheme'),
        'type':fields.selection([
            ('sss','Social Security Service'),
            ('empart','Private Employees'),
            ('empub','Public Employees'),
             ],    'Type former regime', select=True, readonly=False),
        #'voluntary_saving_ids': fields.one2many('voluntary_saving','security_institutions_id',string='Voluntary Savings'),
        'total': fields.function(_total_afp, method=True, type='float', string='Total AFP', readonly=True),
                # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the AFP, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'hr.security.institutions': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the AFP. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'hr.security.institutions': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the AFP. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),    
        'vat': fields.char('Tax id', size=16),
        'apv':fields.boolean('APV authorized'),
        'apvi':fields.boolean('APVI authorized'),
        'apvc':fields.boolean('APVC authorized'),
    }
hr_security_institutions()