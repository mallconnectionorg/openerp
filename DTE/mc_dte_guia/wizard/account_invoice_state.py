#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   DTE Chile OpenERP 7
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

from openerp.osv import osv

import logging

class account_invoice_cancel(osv.osv_memory):
    _inherit = "account.invoice.cancel"

    def invoice_cancel(self, cr, uid, ids, context=None):
        logger = logging.getLogger('invoice_cancel')
        logger.warn('se ejecuta')
        res = super(account_invoice_cancel, self).invoice_cancel(cr, uid, ids, context=context)
        if context is None:
            context = {}
        active_ids = context.get('active_ids', False)
        if active_ids:
            inv_obj = self.pool.get('account.invoice')
            for inv in inv_obj.browse(cr, uid, active_ids):
                if inv.mc_dte_ids:
                    dte_ids = [md.id for md in inv.mc_dte_ids]
                    if len(dte_ids) > 1:
                        raise osv.except_osv("Error","Hay mas de un registro (mc.dte) para este DTE.")
                        return False
                    else:
                        md_obj = self.pool.get('mc.dte')
                        md = md_obj.browse(cr, uid, dte_ids[0])
                        if md.estado_dte != 'Borrador':
                            raise osv.except_osv("Error","No se puede cancelar este documento, tiene un DTE asociado.")
                            return False
        return res

account_invoice_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
