# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from openerp.report import report_sxw

class ot(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ot, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'factura': self.factura,
            'origen': self.origen,
            'destino': self.destino,
            'direccion_destino': self.direccion_destino,
            'codigo_destino': self.codigo_destino,
            'peso': self.peso,
            'tipoe': self.tipoe,
        })

    def factura(self, o):
        res = ''
        if o.ot_type == 'hija':
            if o.picking_id:
                if o.picking_id.sale_id:
                    if o.picking_id.sale_id.invoice_ids:
                        res = ''
                        for inv in o.picking_id.sale_id.invoice_ids:
                            res += inv.number + '\n'
        return res

    def origen(self, o):
        res = ''
        if o.ot_type == 'hija':
            if o.picking_id:
                origen = ''
                for sm in o.picking_id.move_lines:
                    if not origen:
                        origen = sm.location_id.name
                    else:
                        if sm.location_id.name != origen:
                            origen = 'Dist.Origen'
                res = origen
        return res

    def destino(self, o):
        res = ''
        if o.ot_type == 'hija':
            if o.picking_id:
                destino = ''
                for sm in o.picking_id.move_lines:
                    if not destino:
                        destino = sm.location_dest_id.name
                    else:
                        if sm.location_dest_id.name != destino:
                            destino = 'Dist.Destino'
                res = destino
        return res

    def direccion_destino(self, o):
        res = ''
        if o.ot_type == 'hija':
            if o.picking_id:
                if o.picking_id.partner_id:
                    res += o.picking_id.partner_id.street or ''
        return res

    def codigo_destino(self, o):
        res = self.destino(o)
        if res:
            res_lista = res.split()
            if len(res_lista) > 1:
                primera_letra = res_lista[0][0]
                segunda_letra = res_lista[1][0]
                res = str(primera_letra)+str(segunda_letra)
            res = res.upper()
        return res

    def peso(self, o):
        res = 0.0
        if o.ot_type == 'hija':
            if o.picking_id:
                for move in o.picking_id.move_lines:
                    res += move.product_id.weight * move.product_qty
        res = str(res) + ' Kg.'
        return res

    def obtiene_tipo_por_ot(self, o):
        res = 'X'
        if o.picking_id:
            tel = 0
            no_tel = 0
            for move in o.picking_id.move_lines:
                if move.product_id.default_code[0:3] == '10C':
                    tel += 1
                else:
                    no_tel += 1
            if tel and not no_tel:
                res = 'O'
            if not tel and no_tel:
                res = 'U'
        return res

    def tipoe(self, o):
        res = 'X'
        telefonia = 0
        no_telefonia = 0
        mixto = 0
        if o.ot_type == 'padre':
            for oth in o.ot_ids:
                tipo_por_oth = self.obtiene_tipo_por_ot(oth)
                if tipo_por_oth == 'O':
                    telefonia += 1
                if tipo_por_oth == 'U':
                    no_telefonia += 1
                if tipo_por_oth == 'X':
                    mixto += 1

            if mixto == 0 and telefonia > 0 and no_telefonia > 0:
                mixto = 1

            if telefonia > 0:
                res = 'O'
            if no_telefonia > 0:
                res = 'U'
            if mixto > 0:
                res = 'X'
        else:
            res = self.obtiene_tipo_por_ot(o)
        return res

report_sxw.report_sxw('report.etiqueta.stock.orden.transporte', 'stock.orden.transporte', 'addons/stock/report/etiqueta_ot.rml',parser=ot)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
