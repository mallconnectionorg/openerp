#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import time
from datetime import datetime
from dateutil import relativedelta
from hr_payroll.report import report_contribution_register

from openerp.report import report_sxw

class contribution_register_report(report_contribution_register.contribution_register_report):
    def __init__(self, cr, uid, name, context):
        super(contribution_register_report, self).__init__(cr, uid, name, context)
        
from netsvc import Service
del Service._services['report.contribution.register.lines']

report_sxw.report_sxw('report.contribution.register.lines', 'hr.contribution.register', 'l10n_cl_hr_payroll/report/report_contribution_register.rml', parser=contribution_register_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
