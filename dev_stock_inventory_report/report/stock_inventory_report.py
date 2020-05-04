# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from datetime import datetime, timedelta
from odoo import api, models


class stock_inv_report(models.AbstractModel):
    _name = 'report.dev_stock_inventory_report.dev_stock_inventory_template'

    def get_formate_date(self,date=False):
        if date:
            return date.strftime("%d-%m-%Y")
        else:
            date = datetime.now()
            return date.strftime("%d-%m-%Y %H:%M:%S")
            
            
    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['dev.stock.inventory'].browse(data['form'])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.stock.inventory',
            'docs': docs,
            'proforma': True,
            'get_formate_date':self.get_formate_date,
        }
        
        
        
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
