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

class pos_order(osv.Model):
    _inherit = 'pos.order'

    _columns = {
        'cashier_id' : fields.many2one('res.users', 'Cajero', readonly=True),
    }

    _defaults = {
        'cashier_id': lambda self, cr, uid, context: uid,
        'user_id': False,
    }
