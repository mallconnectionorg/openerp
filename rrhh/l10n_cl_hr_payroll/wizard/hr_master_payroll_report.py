##!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   Pedro Arroyo M <parroyo@mallconnection.com>
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


from StringIO import *
import time
from osv import fields,osv
import numpy as np
import base64
from lxml import etree
import openerp.exceptions


class hr_master_payroll(osv.osv):
    '''
    master payroll
    '''
    _name = 'hr.master.payroll'
    _description = 'master payroll'

 
    _columns = {
            'name':fields.char('name', size=64, required=False, readonly=False),
            #TODO : import time required to get currect date
            'state': fields.selection([('choose', 'choose'),   # choose payslip
                           ('get', 'get')]),        # get the file
            'date': fields.date('Date'),
            'group_by':fields.selection([
                ('employee','Employee'),
                ('company','Company'),
                 ],    'Group by'),
#            'payslip_run_id':fields.many2one('hr.payslip.run', 'payslip run', required=False), 
#            'payslip_id':fields.many2one('hr.payslip', 'payslip', required=False),  
            'payslip_ids':fields.many2many('hr.payslip', 'masterpayroll_payslip_rel', 'masterpayroll_id', 'payslip_id', 'payslips'), 
            'file':fields.binary('file', filters=None),  
            'data_ids':fields.one2many('hr.master.payroll.line', 'master_payroll_id', 'detalle', required=False, readonly=True),
            #'details': fields.function(_get_invoices, method=True, type='one2many', string='details', store=False), 
        }

    _defaults = { 
        'state': 'choose',
        'name': 'previred',#poner fecha tambien
        'date':lambda *a: time.strftime('%Y-%m-%d'),  
        }

    

        
    def act_getfile(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        #lang = this.lang if this.lang != NEW_LANG_KEY else False
        #mods = map(lambda m: m.name, this.modules) or ['all']
        #mods.sort()
        data = self.make_data(cr,uid,ids,this,context)
        #exp = self.browse(cr, uid, ids)[0]
        buf = StringIO()
        buf = self.generate_file_export(cr, uid, ids,buf,data, context)
        out = base64.encodestring(buf.getvalue())
        buf.close()
        this.name = "Master_payroll.csv"
        writer = {'state': 'get', 'file': out, 'name':this.name}
        
        if context and len(context['active_ids'])>0:
            slips = self.pool.get('hr.payslip').browse(cr, uid, context['active_ids'])
            writer.update({'payslip_ids': [(6,0,context['active_ids'])]})
            
        self.write(cr, uid, ids, writer, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.master.payroll',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            #'target': 'new',
        }
    
    def make_data(self,cr,uid,ids,this,context):
        def parse_data(employee_name, line_ids):
            res = []
            for item in line_ids:
                empl_name = employee_name.encode('utf8')
                item_name = 'id'+str(item.salary_rule_id.id)+'.sec'+str(item.sequence)+'_'+item.name.encode('utf8')
                res +=[[empl_name,item_name,item.total]]
            
            return res
        
        def parse_data_company(slips):
            
            slip_ids = [str(x.id) for x in slips]
            
            res = []
            
            sql = """select rc.name,hpl.name, sum(total) total 
from hr_payslip_line hpl, hr_payslip hp, res_company rc 
where hpl.slip_id = hp.id and hp.company_id = rc.id and hp.id in (%s)
group by rc.name,hpl.name
order by rc.name, hpl.name""" % (", ".join(slip_ids))
            cr.execute(sql)
            
            for line in cr.fetchall():
                res += [[line[0].encode('utf-8'),line[1].encode('utf-8'),line[2]]]
            
            return res
        
        
        slips=[]
        if context and len(context['active_ids'])>0:
            slips = self.pool.get('hr.payslip').browse(cr, uid, context['active_ids'])
        if len(this.payslip_ids)>0:
            slips = this.payslip_ids
            
        
        data = []
        if this.group_by=='company':
            data = parse_data_company(slips)
        
        elif this.group_by=='employee':
            
            for payslip in slips:
                if len(payslip.line_ids)==0:
                    continue
#                data += parse_data(payslip.name+'_'+payslip.employee_id.name,payslip.line_ids)
                data += parse_data(payslip.name,payslip.line_ids)
                
        if len(data)>0:
            return data
        else:
            raise openerp.exceptions.Warning("Processing has not produced any result. please make sure you have selected payroll and that these movements have to process.")
            
        """if this.payslip_id.id:
            this = this.payslip_id
            
            #for item in this.line_ids:
            #    data +=[[this.employee_id.name.encode('utf8'),item.name.encode('utf8'),item.amount]]
            #return data
            return parse_data(this.employee_id.name, this.line_ids)
        
        if this.payslip_run_id.id:
            for payslip in this.payslip_run_id.slip_ids:
                if len(payslip.line_ids)==0:
                    continue
                data += parse_data(payslip.employee_id.name,payslip.line_ids)
                #for item in payslip.line_ids:
                #    data +=[[payslip.employee_id.name.encode('utf8'),item.name.encode('utf8'),item.amount]]
            return data
        """    
    
    def generate_file_export(self, cr, uid, ids,buf,data, context=None):
        matrix = np.array(data)
        print matrix
        rows, row_pos = np.unique(matrix[:, 0], return_inverse=True,)
        cols, col_pos = np.unique(matrix[:, 1], return_inverse=True,)
        
        pivot_table = np.zeros((len(rows), len(cols)), dtype=object)
        
        #rows =np.append([''],rows)
        rows2=[]
        for i in rows:
            rows2 += [[i]]
        
        pivot_table = np.append(rows2,pivot_table,axis=1)
        cols = np.append([''],cols)
        pivot_table[row_pos, col_pos+1] = matrix[:, 2]
        
        #data = pivot_table.tolist()
        #b = data.insert(0,cols.tolist())
        
        header = ','.join(cols)
        np.savetxt(buf,pivot_table,fmt='%s', delimiter=',',newline=";\n", header = header)
        #with open('test.out', 'r') as file2:
        #    buf = StringIO(file2.read())
        return buf
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res = super(hr_master_payroll,self).read(cr, uid, ids, fields, context, load)  
        return res  

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(hr_master_payroll,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

hr_master_payroll()


class hr_master_payroll_line(osv.osv):
    _name = "hr.master.payroll.line"
    
    _columns = {
            'name':fields.char('Name', size=64, required=False, readonly=False),
            'master_payroll_id':fields.many2one('hr.master.payroll', 'head', required=False), 
                    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(hr_master_payroll_line,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if res['type']=='tree':
            report = self.pool.get(context['active_model']).browse(cr,uid,context['active_ids'])[0] if 'active_model' in context and 'active_ids' in context else None
            if report:
                file = base64.b64decode(report.file)
            
                for col in file.split(';')[0].split(','):
                    clean_col = col.decode('utf8').replace(' ','_')
                    res['fields'][clean_col]={
                                          'selectable': True, 'views': {}, 'type': 'char', 'string': col
                                          }
                                     
                    doc = etree.XML(res['arch'])
                    node = doc.find("tree")
                    child2 = etree.Element("field")
                    print col
                    child2.set('name', clean_col)
                    child2.set('modifiers','{}')
                    doc.append(child2)
                    res['arch'] = etree.tostring(doc)
        return res
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res = super(hr_master_payroll_line,self).read(cr, uid, ids, fields, context, load)  
        #list [{'name': u'previred', 'id': 1}]
        res 
        setids = len(ids)
        report = self.pool.get(context['active_model']).browse(cr,uid,context['active_ids'])[0] if 'active_model' in context and 'active_ids' in context else None
        if report:
            file = base64.b64decode(report.file)
        i = 0
        cols = []
        for row in file.split(';'):
            if i==0:
                cols = row.decode('utf8').replace(' ','_').split(',')
                map= {c: '' for c in cols}
                #cols = map.keys()
                i+=1
                continue
            item={'id': i-1}
            ids.append(i-1) if setids==0 else None
            map2 = map
            i2 = 0
            if len(row)!=1:
                for col in row.split(',') :
                    map2.update({cols[i2]:col})
                    i2+=1
    
                item.update(map2) 
                res.append(item)  
                
                i+=1 
        
        return res     
    
    
    
    
hr_master_payroll_line()

