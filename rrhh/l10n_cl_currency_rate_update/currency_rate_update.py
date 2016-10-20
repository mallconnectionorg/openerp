#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#   Pedro Arroyo M. <parroyo@mallconnection.com>
#   Copyright (C) 2015 Mall Connection(<http://www.mallconnection.org>).
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

from openerp.osv import fields, osv, orm
import time
from datetime import datetime, timedelta
import logging
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons import currency_rate_update as cur_rat_upd
from suds.client import Client
import math

_logger = logging.getLogger(__name__)

class Currency_rate_update_service(osv.Model):
    """Class thats tell for wich services wich currencies
    have to be updated"""
    _inherit = "currency.rate.update.service"
    _description = "Currency Rate Update"
    
    _columns = {
            'username':fields.char('User name'),
            'password':fields.char('Password'),
            'days_backwards': fields.integer('days backwards'),
                    }

    
    
    def __init__(self, pool, cr):
        """Add a new state value"""
        val = super(Currency_rate_update_service, self)
        if val._columns.has_key('service'):
            if not 'bcentral_getter' in dict(super(Currency_rate_update_service, self)._columns['service'].selection):
                super(Currency_rate_update_service, self)._columns['service'].selection.append(('bcentral_getter', 'Banco central of Chile'))
                #val._columns['service'].selection.append(('bcentral_getter', 'Banco central of Chile')) 
                
        #if not 'bcentral_getter' in dict(super(Currency_rate_update_service, self)._columns['service'].selection):
        #    super(Currency_rate_update_service, self)._columns['service'].selection.append(('bcentral_getter', 'Banco central of Chile'))
            
        return super(Currency_rate_update_service, self).__init__(pool, cr)
    
    
Currency_rate_update_service()

class UnknowClassError(Exception):
    def __str__(self):
        return 'Unknown Class'
    def __repr__(self):
        return 'Unknown Class'

class Currency_getter_factory(object):
    """Factory pattern class that will return
    a currency getter class base on the name passed
    to the register method"""
    def register(self, class_name):
        allowed = [
                          'Admin_ch_getter',
                          'PL_NBP_getter',
                          'ECB_getter',
                          'NYFB_getter',
                          'Google_getter',
                          'Yahoo_getter',
                          'Banxico_getter',
                          'CA_BOC_getter',
                          'bcentral_getter',
                    ]
        if class_name in allowed:
            class_def = eval(class_name)
            return class_def()
        else :
            raise UnknowClassError
        

#Currency_getter_factory()
class Yahoo_getter(cur_rat_upd.currency_rate_update.Yahoo_getter):
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        return super(Yahoo_getter, self).get_updated_currency(currency_array, main_currency, max_delta_days)
Yahoo_getter()

class Admin_ch_getter(cur_rat_upd.currency_rate_update.Admin_ch_getter):
    def rate_retrieve(self, dom, ns, curr) :
        return super(Admin_ch_getter,self).rate_retrieve(dom, ns, curr)
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        return super(Admin_ch_getter, self).get_updated_currency(currency_array, main_currency, max_delta_days)
Admin_ch_getter()

class ECB_getter(cur_rat_upd.currency_rate_update.ECB_getter):
    def rate_retrieve(self, dom, ns, curr) :
        return super(ECB_getter,self).rate_retrieve(dom, ns, curr)
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        return super(ECB_getter, self).get_updated_currency(currency_array, main_currency, max_delta_days)
ECB_getter()

class PL_NBP_getter(cur_rat_upd.currency_rate_update.PL_NBP_getter):
    def rate_retrieve(self, dom, ns, curr) :
        return super(PL_NBP_getter,self).rate_retrieve(dom, ns, curr)
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        return super(PL_NBP_getter, self).get_updated_currency(currency_array, main_currency, max_delta_days)
PL_NBP_getter()

class Banxico_getter(cur_rat_upd.currency_rate_update.Banxico_getter):
    def rate_retrieve(self, dom, ns, curr) :
        return super(Banxico_getter,self).rate_retrieve(dom, ns, curr)
    def get_updated_currency(self, currency_array, main_currency, max_delta_days):
        return super(Banxico_getter, self).get_updated_currency(currency_array, main_currency, max_delta_days)
Banxico_getter()

class Currency_rate_update(osv.Model):
    """Class that handle an ir cron call who will
    update currencies based on a web url"""
    _inherit = "currency.rate.update"
    
    def run_currency_update(self, cr, uid):
        "update currency at the given frequence"
        
        def save_rates(self,curr,rate_obj,rate_val,rate_name,do_create=True):
            
            if len(curr.rate_ids)==0:
                rate_obj.create(cr, uid, {'currency_id': curr.id, 'rate':rate_val, 'name': rate_name},{})
            else:
                lidrate = map(lambda x: x.id if x.name == rate_name else None,curr.rate_ids)
                lidrate=dict.fromkeys(lidrate).keys() if dict.fromkeys(lidrate) != {None: None} else None
                #lidrate = [(2, x)  for x in lidrate if x != None]
                if lidrate:
                    rate_obj.unlink(cr,uid,[x  for x in lidrate if x != None])
                    
                rate_obj.create(cr, uid, {'currency_id': curr.id, 'rate':rate_val, 'name': rate_name},{})
            
            #if len(curr.rate_ids)==0:
                #rate_obj.create(cr, uid, {'currency_id': curr.id, 'rate':rate_val, 'name': rate_name})
            #    lidrate.update([(0,0,{'currency_id': curr.id, 'rate':rate_val, 'name': rate_name})])
            #else:
            #    for rate in curr.rate_ids :
            #        lidrate.append([(0,0,{'currency_id': curr.id, 'rate':rate_val, 'name': rate_name})])
                    #if rate.name == rate_name :
                        
                    #    rate.write({'rate':rate_val})
                    #    do_create = False
                    #    break

                    #if do_create :
                    #    rate_obj.create(cr, uid, {'currency_id': curr.id, 'rate':rate_val, 'name': rate_name})
            
           
            

        factory = Currency_getter_factory()
        curr_obj = self.pool.get('res.currency')
        rate_obj = self.pool.get('res.currency.rate')
        companies = self.pool.get('res.company').search(cr, uid, [])
        
        for comp in self.pool.get('res.company').browse(cr, uid, companies):
            ##the multi company currency can beset or no so we handle
            ##the two case
            if not comp.auto_currency_up :
                continue
            #we initialise the multi compnay search filter or not serach filter
            search_filter = []
            if comp.multi_company_currency_enable :
                search_filter = [('company_id','=',comp.id)]
            #we fetch the main currency looking for currency with base = true. The main rate should be set at  1.00
            main_curr_ids = curr_obj.search(cr, uid, [('base','=',True),('company_id','=',comp.id)])
            if not main_curr_ids:
                # If we can not find a base currency for this company we look for one with no company set
                main_curr_ids = curr_obj.search(cr, uid, [('base','=',True),('company_id','=', False)])
            if main_curr_ids:
                main_curr_rec = curr_obj.browse(cr, uid, main_curr_ids[0])
            else:
                raise orm.except_orm(_('Error!'),('There is no base currency set!'))
            if main_curr_rec.rate != 1:
                raise orm.except_orm(_('Error!'),('Base currency rate should be 1.00!'))
            main_curr = main_curr_rec.name
            for service in comp.services_to_use :
                print "comp.services_to_use =", comp.services_to_use
                note = service.note or ''
                try :
                    ## we initalize the class that will handle the request
                    ## and return a dict of rate
                    getter = factory.register(service.service)
                    print "getter =", getter
                    curr_to_fetch = map(lambda x : x.name, service.currency_to_update)
                    res, log_info = getter.get_updated_currency(curr_to_fetch, main_curr, service.max_delta_days) if service.service!='bcentral_getter' else getter.get_updated_currency(curr_to_fetch, main_curr, service.max_delta_days, service.username,service.password,service.days_backwards) 
                    rate_name = time.strftime('%Y-%m-%d')
                    for curr in service.currency_to_update :
                        print curr.name
                        if curr.name == main_curr or curr.name  not in res.keys() :
                            continue
                        do_create = True
                        if type(res[curr.name])==float:
                            save_rates(self,curr,rate_obj,res[curr.name],rate_name)
                        elif type(res[curr.name])==list:
                            for item in res[curr.name]:
                                save_rates(self,curr,rate_obj,item['val'],item['name'])
                            

                    # show the most recent note at the top
                    note = "\n%s currency updated. "\
                       %(datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'))\
                       + note
                    note = (log_info or '') + note
                    service.write({'note':note})
                except Exception, e:
                    error_msg = "\n%s ERROR : %s"\
                        %(datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'), str(e))\
                        + note
                    _logger.info(str(e))
                    service.write({'note':error_msg})
    

class bcentral_getter(cur_rat_upd.currency_rate_update.Curreny_getter_interface):
    """
    Implementacion interface Currency_getter_factory para banco central
    """

    cur_code_suported = {
'THB':'F072.CLP.THB.N.O.D',    'PAB':'F072.CLP.PAB.N.O.D',    'VEB':'F072.CLP.VEB.N.O.D',    'BOL':'F072.CLP.BOL.N.O.D',    'CRC':'F072.CLP.CRC.N.O.D',    'CZK':'F072.CLP.CZK.N.O.D',    
'DKK':'F072.CLP.DKK.N.O.D',    'ISK':'F072.CLP.ISK.N.O.D',    'SKK':'F072.CLP.SKK.N.O.D',    'NOK':'F072.CLP.NOK.N.O.D',    'SEK':'F072.CLP.SEK.N.O.D',    'DEG':'F072.CLP.DEG.N.O.D',    
'AED':'F072.CLP.AED.N.O.D',    'AUD':'F072.CLP.AUD.N.O.D',    'CAD':'F072.CLP.CAD.N.O.D',    'BMD':'F072.CLP.BMD.N.O.D',    'PRE':'F073.TCO.PRE.Z.D',    'FJD':'F072.CLP.FJD.N.O.D',    
'KYD':'F072.CLP.KYD.N.O.D',    'BSP':'F072.CLP.BSP.N.O.D',    'SGD':'F072.CLP.SGD.N.O.D',    'HKD':'F072.CLP.HKD.N.O.D',    'NZD':'F072.CLP.NZD.N.O.D',    'TWD':'F072.CLP.TWD.N.O.D',    
'VND':'F072.CLP.VND.N.O.D',    'EUR':'F072.CLP.EUR.N.O.D',    'HUF':'F072.CLP.HUF.N.O.D',    'XPF':'F072.CLP.XPF.N.O.D',    'CHF':'F072.CLP.CHF.N.O.D',    'PYG':'F072.CLP.PYG.N.O.D',    
'UAH':'F072.CLP.UAH.N.O.D',    'RON':'F072.CLP.RON.N.O.D',    'EGP':'F072.CLP.EGP.N.O.D',    'GBP':'F072.CLP.GBP.N.O.D',    'TRY':'F072.CLP.TRY.N.O.D',    'PEN':'F072.CLP.PEN.N.O.D',    
'ARS':'F072.CLP.ARS.N.O.D',    'COP':'F072.CLP.COP.N.O.D',    'CUP':'F072.CLP.CUP.N.O.D',    'DOP':'F072.CLP.DOP.N.O.D',    'PHP':'F072.CLP.PHP.N.O.D',    'MXN':'F072.CLP.MXN.N.O.D',    
'UYU':'F072.CLP.UYU.N.O.D',    'GTQ':'F072.CLP.GTQ.N.O.D',    'ZAR':'F072.CLP.ZAR.N.O.D',    'BRL':'F072.CLP.BRL.N.O.D',    'IRR':'F072.CLP.IRR.N.O.D',    'SAR':'F072.CLP.SAR.N.O.D',    
'MYR':'F072.CLP.MYR.N.O.D',    'RUR':'F072.CLP.RUR.N.O.D',    'INR':'F072.CLP.INR.N.O.D',    'IDR':'F072.CLP.IDR.N.O.D',    'PKR':'F072.CLP.PKR.N.O.D',    'ILS':'F072.CLP.ILS.N.O.D',    
'ECS':'F072.CLP.ECS.N.O.D',    'KZT':'F072.CLP.KZT.N.O.D',    'KRW':'F072.CLP.KRW.N.O.D',    'JPY':'F072.CLP.JPY.N.O.D',    'CNY':'F072.CLP.CNY.N.O.D',    'PLN':'F072.CLP.PLN.N.O.D',    
'UTM':'F073.UTR.PRE.Z.M',      'UF':'F073.UFF.PRE.Z.D',       'USD':'F073.TCO.PRE.Z.D'
}
    def rate_retrieve(self):        
        pass

    def get_updated_currency(self, currency_array, main_currency, max_delta_days=1,user='',passwd='',days_backwards=1):
        
        wsdl_url="https://si3.bcentral.cl/SieteWs/SieteWS.asmx?wsdl"
        client = Client(wsdl_url)
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        
        #end_date = datetime.date().today() + datetime.timedelta(days=max_delta_days-1)

        fini=(datetime.today()- timedelta(days=days_backwards-1)).strftime("%Y-%m-%d") if days_backwards>0 else datetime.today().strftime("%Y-%m-%d")
        fend=(datetime.today()+ timedelta(days=max_delta_days-1)).strftime("%Y-%m-%d")
        
        arrayofstring = client.factory.create('ArrayOfString')
        
        #user="154006214"
        #passwd="aXrSxDhS"
        log = ""
        for curr in currency_array: 
            if curr in self.cur_code_suported.keys():
                arrayofstring.string = self.cur_code_suported[curr]
                res = client.service.GetSeries(user,passwd,fini,fend,arrayofstring)
                #print curr, res
                if res.Codigo==0:
                    dserie = []
                    for obs in res.Series.fameSeries[0].obs:
                        d = datetime.strptime(obs.indexDateString, "%d-%m-%Y")
                        if not math.isnan(obs.value):
                            dserie.append({'val':1/obs.value,'name':datetime.strftime(d, '%Y-%m-%d')})
                    #val = res.Series.fameSeries[0].obs[0].value
                    self.updated_currency[curr] = dserie
                    print self.updated_currency
                else:
                    log+="\n%s Cod: %s, msg: %s, curr: %s"%(datetime.strftime(datetime.today(), '%Y-%m-%d %H:%M:%S'), res.Codigo, res.Descripcion,curr)
            
        self.log_info+=log    
        return self.updated_currency, self.log_info
        
            

bcentral_getter()


class res_currency(osv.osv):
    
    def _current_rate(self, cr, uid, ids, name, arg, context=None):
        return super(res_currency,self)._current_rate(cr, uid, ids, name, arg, context)
    
    def _current_rate_silent(self, cr, uid, ids, name, arg, context=None):
        return super(res_currency,self)._current_rate_silent(cr, uid, ids, name, arg, context)
    
    _name = "res.currency"
    _description = "Currency"
    _inherit = "res.currency"
    _columns = {
        'rate': fields.function(_current_rate, string='Current Rate', digits_compute=dp.get_precision('Currency'),
            help='The rate of the currency to the currency of rate 1.'),

        # Do not use for computation ! Same as rate field with silent failing
        'rate_silent': fields.function(_current_rate_silent, string='Current Rate', digits_compute=dp.get_precision('Currency'),
            help='The rate of the currency to the currency of rate 1 (0 if no rate defined).'),

            }

    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount,
                round=True, currency_rate_type_from=False, currency_rate_type_to=False, context=None):
        from_currency_id = from_currency_id[0] if type(from_currency_id) is list else from_currency_id or None
        to_currency_id = to_currency_id[0] if type(to_currency_id) is list else to_currency_id or None
        return super(res_currency, self).compute(cr, uid, from_currency_id, to_currency_id, from_amount, round, currency_rate_type_from, currency_rate_type_to, context)
        #return super(res_currency,self)._current_rate(cr, uid, ids, name, arg, context)
        
res_currency()

class res_currency_rate(osv.osv):
    _inherit = "res.currency.rate"
    _description = "Currency Rate"
    
    _columns = {
                'rate': fields.float('Rate', digits_compute=dp.get_precision('Currency')),
                }
    
res_currency_rate()