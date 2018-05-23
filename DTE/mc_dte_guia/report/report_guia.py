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

import time
import pooler
import logging

from report import report_sxw
from osv import osv

class report_guia_webkit(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        logger = logging.getLogger('report_guia_webkit_init')
        logger.warn('se ejecuta')
        super(report_guia_webkit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'dicc_imp': self.dicc_imp,
        })

    def dicc_imp(self, pick):
        dte_util_obj = pooler.get_pool(self.cr.dbname).get('mc.dte.utilidades')
        res = dte_util_obj.dicc_imp_guia(self.cr, self.uid, pick)
        return res

report_sxw.report_sxw('report.guia.webkit',
                       'stock.picking.out', 
                       'addons/mc_dte_guia/report/report_guia.mako',
                       parser=report_guia_webkit)

