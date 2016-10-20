#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Cesar Lopez
#   Copyright (C) 2011 Mall Connection(<http://www.mallconnection.org>).
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
from openerp.osv import fields, osv, orm
from openerp.addons.base.res.res_partner import format_address
from openerp import netsvc, tools

class res_partner(osv.osv, format_address):
    _inherit = "res.partner"

    def name_get(self, cr, uid, ids, context=None):
        res = super(res_partner, self).name_get(cr, uid, ids, context=context)
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, uid, [('ref','ilike',name)])
        if ids:
            res = self.name_get(cr, uid, ids, context)
        else:
            res = super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
        return res

    def _default_ubicacion_destino_id(self, cr, uid, context=None):
        location_xml_id = 'stock_location_customers'
        mod_obj = self.pool.get('ir.model.data')
        location_id = False
        if location_xml_id:
            try:
                location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                with tools.mute_logger('openerp.osv.orm'):
                    self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
            except (orm.except_orm, ValueError):
                location_id = False
        return location_id

    _columns = {
        'ubicacion_destino_id': fields.many2one('stock.location', 'Ubicacion destino'),
    }

    _defaults = {
        'ubicacion_destino_id': _default_ubicacion_destino_id,
    }
