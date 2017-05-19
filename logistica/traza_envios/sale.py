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
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

class correos_notificacion_tiendas(osv.Model):
    _name = "correos.notificacion.tiendas"

    _columns = {
        'name': fields.char('Correo', size=64),
        'shop_id': fields.many2one('sale.shop', 'Tienda'),
    }

class sale_shop(osv.osv):
    _inherit = "sale.shop"

    _columns = {
        'correo_notificacion_ids': fields.one2many('correos.notificacion.tiendas','shop_id','Correos Notificacion'),
    }

sale_shop()

