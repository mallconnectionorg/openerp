#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import monto_a_texto
from openerp.report import report_sxw
from hr_payroll.report import report_payslip

import logging

class payslip_report(report_payslip.payslip_report):

    def __init__(self, cr, uid, name, context):
        super(payslip_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'disclaimer': self.disclaimer,
            'formatoNumero': self.formatoNumero,
            'nombre_nomina': self.nombre_nomina,
            'formatoFecha': self.formatoFecha,
            'direccion': self.direccion,
            'direccion_compania': self.direccion_compania,
        })

    def mes_texto(self, mes, anio):
        if mes:
            if mes == '01':
                res = 'Enero'
            elif mes == '02':
                res = 'Febrero'
            elif mes == '03':
                res = 'Marzo'
            elif mes == '04':
                res = 'Abril'
            elif mes == '05':
                res = 'Mayo'
            elif mes == '06':
                res = 'Junio'
            elif mes == '07':
                res = 'Julio'
            elif mes == '08':
                res = 'Agosto'
            elif mes == '09':
                res = 'Septiembre'
            elif mes == '10':
                res = 'Octubre'
            elif mes == '11':
                res = 'Noviembre'
            elif mes == '12':
                res = 'Diciembre'
            else:
                res = ''
            res = res + ' ' + anio
            return res
        else:
            res = ''
            return res

    def nombre_periodo(self, nomina):
        try:
            fecha_desde = nomina.date_from
            fecha_desde = fecha_desde.split('-')
            mes = fecha_desde[1]
            anio = fecha_desde[0]
            res = self.mes_texto(mes, anio)
        except:
            res = ''
        return res

    def nombre_nomina(self, obj):
        trabajador = obj.employee_id.name
        periodo = self.nombre_periodo(obj)
        res = u'Liquidación ' + trabajador + ' ' +periodo
        return res

    def formatoFecha(self, fecha_texto):
        logger = logging.getLogger('log.formatoFecha')
        try:
            fecha_texto = fecha_texto.split('-')
            dia = fecha_texto[2]
            mes = fecha_texto[1]
            anio = fecha_texto[0]
            res = dia + '/' + mes + '/' + anio
        except:
            res = ''
        logger.warn(res)
        return res

    def formatoNumero(self, numero):
        numero = str(int(numero))
        nn = ''
        negativo = False
        if '-' in numero:
            negativo = True
            numero = str(abs(int(float(numero))))
        largo_cadena = float(len(numero))
        if largo_cadena % 3 == 0:
            rango = int(largo_cadena / 3)
        else:
            rango = int(largo_cadena / 3) + 1
        for i in range(rango):
            if len(numero) >= 3:
                if nn == '':
                    nn += numero[-3:]
                else:
                    nn = numero[-3:] + '.' + nn
                numero = numero[:-3]
            else:
                if nn:
                    nn = numero + '.' + nn
                else:
                    nn = numero
        if nn:
            if negativo:
                nn = '-' + nn
            res = nn
        else:
            res = numero
        return res

    def disclaimer(self, payslip, cur):
        line_ids = payslip.line_ids
        company_name = payslip.contract_id.company_id.name
        amount = 0
        if line_ids:            
                amount =  sum([line.total for line in  line_ids if line.code == 'liquido'])  
                     
        text = 'Certifico que he recibido de ' + company_name + ' a mi entera satisfaccion la cantidad de '
        text = text + monto_a_texto.amount_to_text(amount, 'es', cur)
        text = text + ' indicado  en la presente liquidacion y no tengo cargo ni cobro alguno que hacer por ninguno de los conceptos correspondidos en ella.'
        return text

    def direccion(self, empleado=None):
        res = ''
        if empleado:
            direccion = empleado.address_home_id or False
            if direccion:
                calle = direccion.street or ''
                comuna = direccion.state_id and direccion.state_id.name or ''
                ciudad = direccion.city or ''
                res = calle + ', ' + comuna + ', ' + ciudad
        return res

    def direccion_compania(self, compania):
        res = ''
        if compania:
            calle = compania.street or ''
            comuna = compania.state_id and compania.state_id.name or ''
            ciudad = compania.city or ''
            if calle and comuna and ciudad:
                res = calle + ', ' + comuna + ', ' + ciudad
            else:
                res = u'OHiggins 241, OF 810, Concepción'
        return res

from netsvc import Service
del Service._services['report.payslip']


report_sxw.report_sxw('report.payslip', 'hr.payslip', 'mc_calculo_comisiones/report/report_payslip.rml', parser=payslip_report)
