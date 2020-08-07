#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Informes XLS
#   Copyright (C) 2020 Cesar Lopez Aguillon
#   Mall Connection
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
from openerp.osv import fields, osv
from openerp import tools

try:
    import json
except ImportError:
    import simplejson as json

import logging

class mc_informes_xls(osv.osv_memory):
    _name = 'mc.informes.xls'

    LISTA_LIBRO_BALANCE = [
        ('libro_mayor', 'Libro mayor'),
        ('libro_diario', 'Libro diario'),
        ('libro_retenciones', 'Libro retenciones'),
        ('balance_general_periodo', 'Balance general del periodo'),
        ('balance_ocho_columnas', 'Balance ocho columnas'),
        ('inventario_balance', 'Inventario y balance'),
    ]

    _columns = {
        'compania_id': fields.many2one('res.company',u'Compañía', required=True, readonly=True),
        'periodo_id': fields.many2one('account.period','Periodo', required=True, domain="[('company_id', '=', compania_id)]"),
        'tipo': fields.selection([('librobalance',u'Libro/Balance'),('cuenta',u'Cuenta')],u'Tipo', required=True),
        'cuenta_id': fields.many2one('account.account','Cuenta', domain="[('company_id', '=', compania_id)]"),
        'libro_balance': fields.selection(LISTA_LIBRO_BALANCE,u'Libro/Balance'),
        'nivel': fields.selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],'Nivel'),
        'mostrar_cuentas': fields.selection([('1', 'Todas'), ('2', 'Con Movimientos')],'Mostrar Cuentas'),
        'periodo_hasta_id': fields.many2one('account.period','Periodo hasta', domain="[('company_id', '=', compania_id)]"),
    }

    _defaults = {
        'nivel' : '6',
        'mostrar_cuentas' : '2',
        'compania_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }

    def _check_cuenta(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #if len(ids) > 1:
        #    return False
        
        assert len(ids) == 1, False
        
        informe = self.browse(cr, uid, ids[0], context=context)
        if informe.tipo == 'cuenta':
            if not informe.cuenta_id:
                return False
        else:
            if informe.cuenta_id:
                return False
        return True

    def _check_libro_balance(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #if len(ids) > 1:
        #    return False
        
        assert len(ids) == 1, False
        
        informe = self.browse(cr, uid, ids[0], context=context)
        if informe.tipo == 'librobalance':
            if not informe.libro_balance:
                return False
        else:
            if informe.libro_balance:
                return False
        return True

    _constraints = [
        (_check_cuenta, u'¡Error!\nNo debe ingresar cuenta si el tipo de reporte es Libro/Balance y debe ingresarla si el tipo es Cuenta.', ['cuenta_id']),
        (_check_libro_balance, u'¡Error!\nNo debe ingresar Libro/Balance si el tipo de reporte es Cuenta y debe ingresarlo si el tipo es Libro/Balance.', ['libro_balance']),
    ]

    def nombre_reporte(self, cr, uid, informe):
        res = 'cuenta'
        if informe.libro_balance:
            res = informe.libro_balance
        return res

    def descargar_informe(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Debe descargar una plantilla a la vez.'
        inf = self.browse(cr, uid, ids[0])
        res = dict()
        repjson = dict()
        repjson['dbname'] = cr.dbname
        repjson['user'] = uid
        repjson['tipo'] = inf.tipo
        repjson['cuenta_id'] = inf.cuenta_id and inf.cuenta_id.id or False
        repjson['periodo_id'] = inf.periodo_id.id
        repjson['periodo_hasta_id'] = inf.periodo_hasta_id and inf.periodo_hasta_id.id or False
        repjson['compania_id'] = inf.compania_id.id
        repjson['reporte'] = self.nombre_reporte(cr, uid, inf)
        repjson['nivel'] = inf.nivel
        repjson['mostrar_cuentas'] = inf.mostrar_cuentas
        repjson = json.dumps(repjson)
        if repjson:
            url = '/web/binary/descargar_informes_xls?data=' + repjson
            res['type'] = 'ir.actions.act_url'
            res['url'] = url
            res['target'] = 'self'
        return res

mc_informes_xls()
