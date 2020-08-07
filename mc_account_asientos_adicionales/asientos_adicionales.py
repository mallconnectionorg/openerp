#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Asientos adicionales
#   Copyright (C) 2020 Cesar Lopez Aguillon Mall Connection
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

from osv import fields, osv, orm
from openerp import SUPERUSER_ID

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'add_move_id': fields.many2one('account.move', 'Asiento adicional', select=True, readonly=True),
    }

    def crear_lineas_asiento(self, cr, uid, linea_factura, am_id, aa_obj):
        
        cvals1 = dict()
        cvals2 = dict()
        
        costo = 0.0
        if linea_factura.product_id.product_tmpl_id.standard_price:
            costo = linea_factura.quantity * linea_factura.product_id.product_tmpl_id.standard_price
        
        if aa_obj.pasa_al == 'debe':
            cvals1['debit'] = costo
            cvals2['credit'] = costo
        elif aa_obj.pasa_al == 'haber':
            cvals2['debit'] = costo
            cvals1['credit'] = costo
        else:
            cvals2['debit'] = 0.0
            cvals1['credit'] = 0.0
        
        nombre = self.pool.get('ir.sequence').get(cr, uid, 'lineas.asientos.adicionales')
        
        cuenta1 = aa_obj.cuenta_desde_id and aa_obj.cuenta_desde_id.id or False
        cuenta2 = aa_obj.cuenta_hacia_id and aa_obj.cuenta_hacia_id.id or False
        # primero crear la linea de la cuenta costo
        cvals1['name'] = nombre
        cvals1['move_id'] = am_id
        cvals1['account_id'] = cuenta1
        # despues crear la linea de la cuenta mercaderias
        if linea_factura.product_id.default_code:
            nombre = nombre + '-[' + linea_factura.product_id.default_code + ']'
        else:
            nombre = nombre + '[PROD]'
        cvals2['name'] = nombre
        cvals2['move_id'] = am_id
        cvals2['account_id'] = cuenta2
        
        move_line_obj = self.pool.get('account.move.line')
        
        move_line_obj.create(cr, uid, cvals1)
        move_line_obj.create(cr, uid, cvals2)
        
        return True

    # account.move = asiento
    # account.move.line = lineas de asiento
    def crear_asiento(self, cr, uid, ids, context=None):
        aa_ids = self.pool.get('mc.asiento.adicional').search(cr, uid, [])
        if not aa_ids:
            return True
        aa_id = aa_ids[0]
        aa_obj = self.pool.get('mc.asiento.adicional').browse(cr, uid, aa_id)
        for factura in self.browse(cr, uid, ids):
            # crear asiento
            cvals = dict()
            cvals['name'] = factura.number
            cvals['journal_id'] = aa_obj.diario_id.id
            am_id = self.pool.get('account.move').create(cr, uid, cvals)
            
            for lf in factura.invoice_line:
                # crear lineas de asiento
                self.crear_lineas_asiento(cr, uid, lf, am_id, aa_obj)
                
            self.write(cr, uid, [factura.id], {'add_move_id': am_id}, context=context)
            self.pool.get('account.move').post(cr, uid, [am_id], context=context)
        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        self.crear_asiento(cr, uid, ids, context)
        return super(account_invoice, self).invoice_validate(cr, uid, ids, context)

account_invoice()

class mc_asiento_adicional(osv.osv):
    _name = 'mc.asiento.adicional'

    _columns = {
        'name': fields.char('Nombre', size=128),
        'diario_id': fields.many2one('account.journal', 'Diario', select=True),
        'cuenta_desde_id': fields.many2one('account.account', 'Cuenta desde', select=True),
        'cuenta_hacia_id': fields.many2one('account.account', 'Cuenta hacia', select=True),
        'pasa_al': fields.selection([
            ('debe','Debe'),
            ('haber','Haber'),
            ],'Pasa al', help="Puede ser el debe o al haber."),

    }

mc_asiento_adicional()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
