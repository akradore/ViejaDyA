# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

from odoo import api, fields, models, _
import base64
import csv
from io import StringIO
from io import BytesIO
from xlwt import easyxf
import xlrd


class import_inventory_lines(models.TransientModel):
    _name = "import.inventory.lines"


    file_type = fields.Selection([('excel','Excel'),('csv','CSV')],string='File Type', default='csv')
    csv_file = fields.Binary(string='File')
    
    @api.multi
    def import_line(self):
        data=[]
        if self.file_type == 'excel':
            file_datas = base64.decodestring(self.csv_file) 
            workbook = xlrd.open_workbook(file_contents=file_datas)
            sheet = workbook.sheet_by_index(0)
            data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
            data.pop(0)
        else:
            file_data = base64.decodestring(self.csv_file)
            s_data = str(file_data.decode("utf-8")) 
            s_data = s_data.split('\n')
            data =[]
            for d in s_data:
                if d:
                    data.append(d.split(','))
            data.pop(0)
        count=0
        note=''
        for line in data:
            count += 1
            product_id = self.env['product.product'].search([('default_code','=',line[0])],limit=1)
            
            active_id = self._context.get('active_id')
            stock_inv = self.env['stock.inventory'].browse(active_id)
            l_id = stock_inv.location_id
            

            if product_id:
                vals={
                    'product_id':product_id.id or False,
                    'location_id':l_id.id,
                    'product_qty':line[1] or '',
                    'inventory_id' :stock_inv.id or False,
                }
                self.env['stock.inventory.line'].create(vals)
            else:
                if not note:
                    note = "Product Not found in uploaded CSV.\n"
                note += "Line no :"+str(count)+ " Product Code :"+str(line[0])+"\n"
        if note:
            log_id=self.env['inventory.log'].create({'name':note})
            return {
                'view_mode': 'form',
                'res_id': log_id.id,
                'res_model': 'inventory.log',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    
