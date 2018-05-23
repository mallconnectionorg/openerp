#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Punto de Venta MC
#   Copyright (C) 2016 Cesar Lopez Aguillon Mall Connection
#   <http://www.mallconnection.org>.
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

from osv import osv, fields

class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'shop_id' : fields.many2one('sale.shop', 'Tienda'),
        'shop_ids': fields.many2many('sale.shop', 'users_pos_rel', 'user_id', 'shop_id', 'Tiendas'),
    }

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        ids = []
        if name:
            ids = self.search(cr, user, [('login','=',name)]+ args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
