# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################


from io import BytesIO
from datetime import datetime
from datetime import timedelta
from odoo import models, fields,api, _
import xlwt
from xlwt import easyxf
import base64
import itertools
from operator import itemgetter
import operator

class dev_stock_inventory(models.TransientModel):
    _name = "dev.stock.inventory"

    @api.model
    def _get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company',string='Company',required="1", default=_get_company_id)
    warehouse_ids = fields.Many2many('stock.warehouse',string='Warehouse',required="1")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    filter_by = fields.Selection([('product','Product'),('category','Product Category')],string='Filter By', default='product')
    category_id = fields.Many2one('product.category',string='Category')
    product_ids = fields.Many2many('product.template',string='Products', domain=[('type','=','product')])
    is_group_by_category = fields.Boolean('Group By Category')
    is_zero = fields.Boolean('With Zero Values')
    excel_file = fields.Binary('Excel File')


    def get_product(self):
        product_pool=self.env['product.product']
        if not self.filter_by:
            product_ids = product_pool.search([('type','=','product')])
            return product_ids
        elif self.filter_by == 'product' and self.product_ids:
            product_ids = product_pool.search([('type','=','product'),('product_tmpl_id','in',self.product_ids.ids)])
            print ("======",product_ids)
            return product_ids
        elif self.filter_by == 'category':
            if self.category_id:
                product_ids = product_pool.search([('categ_id','child_of',self.category_id.id),('type','=','product')])
                return product_ids
            else:
                product_ids = product_pool.search([('type','=','product')])
                return product_ids
            
        return []

    @api.multi
    def group_by_lines(self,lst):
        n_lst = sorted(lst, key=itemgetter('category'))
        groups = itertools.groupby(n_lst, key=operator.itemgetter('category'))
        group_lines = [{'category': k, 'values': [x for x in v]} for k, v in groups]
        return group_lines

    
    
    # This method return the beginning Quantity of product
    @api.multi
    def get_beginning_qty(self,product,warehouse_id):
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        date = start_date - timedelta(days=1)
        date = date.strftime("%Y-%m-%d")
        date = date + ' 23:59:59'
        if date:
            product = product.with_context(to_date=date)
        if warehouse_id:
            product = product.with_context(warehouse=[warehouse_id.id])

        return product.qty_available
        
        
    # This method return the Receive Quantity of product between start and end date
    @api.multi
    def get_sale_purchase_qty(self, product, warehouse_id,move_type, start_date, end_date):
        state = 'done'
        location_ids = self.env['stock.location'].search([('id','child_of',warehouse_id.lot_stock_id.id)])
        m_type = ''
        if move_type == 'outgoing':
            m_type = 'and sm.location_id in %s'
        if move_type == 'incoming':
            m_type = 'and sm.location_dest_id in %s'
        
        query = """ select sum(sm.product_uom_qty) from stock_move as sm \
                    JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                    JOIN product_product as pp ON pp.id = sm.product_id \
                    where sm.date >= %s and sm.date <= %s and spt.warehouse_id = %s \
                    and sm.product_id = %s"""+ m_type +""" \
                    and sm.state = %s and sm.company_id = %s """
        params = (start_date, end_date, warehouse_id.id, product.id,tuple(location_ids.ids), state,self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0
        
        
    # This method returns the Internal IN / OUT Quantity of product between start and end Dates
    @api.multi
    def get_internal_qty(self, product, warehouse_id,internal_type, start_date, end_date):
        m_type = ''
        main_location = warehouse_id.lot_stock_id
        location_ids = self.env['stock.location'].search([('location_id','child_of',main_location.id)])
        if internal_type == 'out':
            m_type = 'and sm.location_id in %s'
        else:
            m_type = 'and sm.location_dest_id in %s'

        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                              JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date >= %s and sm.date <= %s and spt.warehouse_id = %s \
                              and spt.code = %s """ + m_type + """and sm.product_id = %s \
                              and sm.state = %s and sm.company_id = %s
                              """

        params = (start_date, end_date, warehouse_id.id, 'internal', tuple(location_ids.ids), product.id, 'done',
                  self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum') or 0
        return 0.0
        
        
    # This method returns the Production IN / OUT Quantity of product between start and end Dates
    @api.multi
    def get_production_qty(self, product, warehouse_id,production_type, start_date, end_date):
        m_type = ''
        location_id = product.property_stock_production.id
        stock_location_ids = self.env['stock.location'].search([('location_id','child_of',warehouse_id.lot_stock_id.id)])
        if production_type == 'out':
            m_type = 'and sm.location_dest_id = %s and sm.location_id in %s'
        else:
            m_type = 'and sm.location_id = %s and sm.location_dest_id in %s'

        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                  JOIN product_product as pp ON pp.id = sm.product_id \
                  where sm.date >= %s and sm.date <= %s \
                  """ + m_type + """and sm.product_id = %s and sm.state = %s and sm.company_id = %s """

        params = (start_date, end_date, location_id, tuple(stock_location_ids.ids), product.id, 'done', self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum') or 0
        return 0.0
        
        
    # This method returns the Adjustment Quantity of product between start and end Dates
    @api.multi
    def get_adjustment_qty(self, product, warehouse_id, start_date, end_date):
        location_id = product.property_stock_inventory.id
        stock_location_ids = self.env['stock.location'].search([('location_id','child_of',warehouse_id.lot_stock_id.id)])
        in_qty = 0
        out_qty = 0
        if location_id:    
            query = """select sum(sm.product_uom_qty) from stock_move as sm \
                      JOIN product_product as pp ON pp.id = sm.product_id \
                      where sm.date >= %s and sm.date <= %s and location_id in %s and \
                      sm.location_dest_id = %s and sm.product_id = %s and sm.picking_type_id is null\
                      and sm.group_id is null and sm.state = %s and sm.company_id = %s
                      """

            params = (start_date, end_date, tuple(stock_location_ids.ids), location_id, product.id, 'done', self.company_id.id)

            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            if result[0].get('sum'):
                out_qty = result[0].get('sum')
            
            
            query = """select sum(sm.product_uom_qty) from stock_move as sm \
                      JOIN product_product as pp ON pp.id = sm.product_id \
                      where sm.date >= %s and sm.date <= %s and location_dest_id in %s and \
                      sm.location_id = %s and sm.product_id = %s and sm.picking_type_id is null\
                      and sm.group_id is null and sm.state = %s and sm.company_id = %s
                      """

            params = (start_date, end_date, tuple(stock_location_ids.ids), location_id, product.id, 'done', self.company_id.id)

            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            if result[0].get('sum'):
                in_qty = result[0].get('sum')
            
            
        qty = in_qty - out_qty
        return qty
        
    
    @api.multi
    def get_lines(self,warehouse_id):
        lst=[]
        product_ids = self.get_product()
        start_date = self.start_date + ' 00:00:00'
        end_date = self.end_date + ' 23:59:59'
        for product in product_ids:
            beginning_qty = self.get_beginning_qty(product, warehouse_id)
            
            received_qty = self.get_sale_purchase_qty(product, warehouse_id, 'incoming', start_date, end_date) or 0.0
            
            sale_qty = self.get_sale_purchase_qty(product, warehouse_id, 'outgoing', start_date, end_date) or 0.0
            
            internal_out_qty = self.get_internal_qty(product, warehouse_id, 'out', start_date, end_date) or 0.0
            
            internal_in_qty = self.get_internal_qty(product, warehouse_id, 'in', start_date, end_date) or 0.0
            
            production_out_qty = self.get_production_qty(product, warehouse_id,'out', start_date, end_date)
            
            production_qty = self.get_production_qty(product, warehouse_id,'in', start_date, end_date)
            
            adjust_qty = self.get_adjustment_qty(product, warehouse_id, start_date, end_date)
            
            ending_qty = (beginning_qty + received_qty + adjust_qty + production_qty) - production_out_qty - sale_qty + internal_in_qty - internal_out_qty
            if not self.is_zero:
                if beginning_qty != 0 or received_qty != 0 or sale_qty != 0 or  adjust_qty != 0 or ending_qty != 0 or internal_in_qty != 0 or internal_out_qty != 0:
                    lst.append({
                        'category':product.categ_id.name or 'Untitle',
                        'product':product.display_name,
                        'beginning_qty':beginning_qty,
                        'received_qty':received_qty,
                        'sale_qty':sale_qty,
                        'internal_out_qty':internal_out_qty,
                        'internal_in_qty': internal_in_qty,
                        'production_qty':production_qty,
                        'production_out_qty':production_out_qty,
                        'adjust_qty':adjust_qty,
                        'ending_qty':ending_qty,
                        'cost':product.standard_price,
                        'total_cost':product.standard_price * ending_qty,
                    })
            else:
                lst.append({
                    'category': product.categ_id.name or 'Untitle',
                    'product': product.display_name,
                    'beginning_qty': beginning_qty,
                    'received_qty': received_qty,
                    'sale_qty': sale_qty,
                    'internal_out_qty': internal_out_qty,
                    'internal_in_qty': internal_in_qty,
                    'production_qty':production_qty,
                    'production_out_qty':production_out_qty,
                    'adjust_qty': adjust_qty,
                    'ending_qty': ending_qty,
                    'cost':product.standard_price,
                    'total_cost':product.standard_price * ending_qty,
                    
                })
                print ('======',lst)
        return lst

        
    @api.multi
    def print_pdf(self):
        data = self.read()
        datas = {
            'form': self.id
        }
        return self.env.ref('dev_stock_inventory_report.print_dev_stock_inventory').report_action(self, data=datas)


    @api.multi
    def export_stock_ledger(self):
        workbook = xlwt.Workbook()
        filename = 'Stock Inventory.xls'
        # Style
        main_header_style = easyxf('font:height 400;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz left;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 150; align: horiz left;' "borders: top thin,bottom thin")
        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin")
        text_right_bold1 = easyxf('font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin", num_format_str='0.00')
        text_center = easyxf('font:height 150; align: horiz center;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 150; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')

        worksheet = []
        for l in range(0, len(self.warehouse_ids)):
            worksheet.append(l)
        work=0
        for warehouse_id in self.warehouse_ids:
            worksheet[work] = workbook.add_sheet(warehouse_id.name)
            for i in range(0, 12):
                worksheet[work].col(i).width = 140 * 30
                if i == 9:
                    worksheet[work].col(i).width = 160 * 30
            
            worksheet[work].set_panes_frozen(True)
            worksheet[work].set_horz_split_pos(9) 
            worksheet[work].set_vert_split_pos(3)

            worksheet[work].write_merge(0, 1, 0, 9, 'STOCK INVENTORY', main_header_style)

            col=2
            worksheet[work].write(4, col, 'Company', header_style)
            worksheet[work].write(4, col+1, 'Warehouse', header_style)
            worksheet[work].write(4, col+2, 'Start Date', header_style)
            worksheet[work].write(4, col+3, 'End Date', header_style)
            worksheet[work].write(4, col+4, 'Generated By', header_style)
            worksheet[work].write(4, col+5, 'Generated Date', header_style)



            worksheet[work].write(5, col, self.company_id.name, text_center)
            worksheet[work].write(5, col+1, warehouse_id.name, text_center)
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
            start_date = start_date.strftime("%d-%m-%Y")
            worksheet[work].write(5, col+2, start_date, text_center)
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
            end_date = end_date.strftime("%d-%m-%Y")
            worksheet[work].write(5, col+3, end_date, text_center)
            worksheet[work].write(5, col+4, self.env.user.name, text_center)
            g_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            worksheet[work].write(5, col+5, g_date, text_center)



            tags = ['Beginning', 'Purchases', 'Sales', 'Internal IN Qty', 'Internal OUT Qty','Production IN Qty', 'Production OUT Qty', 'Adjustments', 'Ending', 'Cost', 'Total Cost']

            r= 8
            worksheet[work].write_merge(r, r, 0, 2, 'Products', header_style)
            c = 3
            for tag in tags:
                worksheet[work].write(r, c, tag, header_style)
                c+=1

            lines=self.get_lines(warehouse_id)
            if not self.is_group_by_category:
                r=9
                b_qty = r_qty = s_qty = i_qty = p_qty = po_qty = a_qty = e_qty = o_qty = cost= total_cost = 0
                for line in lines:
                    b_qty += line.get('beginning_qty')
                    r_qty += line.get('received_qty')
                    s_qty += line.get('sale_qty')
                    i_qty += line.get('internal_in_qty')
                    o_qty += line.get('internal_out_qty')
                    a_qty += line.get('adjust_qty')
                    p_qty += line.get('production_qty')
                    po_qty += line.get('production_out_qty')
                    e_qty += line.get('ending_qty')
                    cost += line.get('cost')
                    total_cost += line.get('total_cost')
                    worksheet[work].write_merge(r, r, 0, 2, line.get('product'), text_left)
                    c=3
                    worksheet[work].write(r, c, line.get('beginning_qty'), text_right)
                    c+=1
                    worksheet[work].write(r, c, line.get('received_qty'), text_right)
                    c+=1
                    worksheet[work].write(r, c, line.get('sale_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('internal_in_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('internal_out_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('production_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('production_out_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('adjust_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('ending_qty'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('cost'), text_right)
                    c += 1
                    worksheet[work].write(r, c, line.get('total_cost'), text_right)
                    r+=1
                worksheet[work].write_merge(r, r, 0, 2, 'TOTAL', text_right_bold)
                c = 3
                worksheet[work].write(r, c, b_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, r_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, s_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, i_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, o_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, p_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, po_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, a_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, e_qty, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, cost, text_right_bold1)
                c += 1
                worksheet[work].write(r, c, total_cost, text_right_bold1)
                r += 1
            else:
                lines = self.group_by_lines(lines)
                r = 9
                for l_val in lines:
                    worksheet[work].write_merge(r, r, 0, 12, l_val.get('category'), group_style)
                    r+=1
                    b_qty = r_qty = s_qty = i_qty = p_qty = po_qty = a_qty = e_qty = o_qty = cost = total_cost = 0
                    for line in l_val.get('values'):
                        b_qty += line.get('beginning_qty')
                        r_qty += line.get('received_qty')
                        s_qty += line.get('sale_qty')
                        i_qty += line.get('internal_in_qty')
                        o_qty += line.get('internal_out_qty')
                        p_qty += line.get('production_qty')
                        po_qty += line.get('production_out_qty')
                        a_qty += line.get('adjust_qty')
                        e_qty += line.get('ending_qty')
                        cost += line.get('cost')
                        total_cost += line.get('total_cost')
                        worksheet[work].write_merge(r, r, 0, 2, line.get('product'), text_left)
                        c = 3
                        worksheet[work].write(r, c, line.get('beginning_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('received_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('sale_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('internal_in_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('internal_out_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('production_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('production_out_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('adjust_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('ending_qty'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('cost'), text_right)
                        c += 1
                        worksheet[work].write(r, c, line.get('total_cost'), text_right)
                        r += 1
                    worksheet[work].write_merge(r, r, 0, 2, 'TOTAL', text_right_bold)
                    c = 3
                    worksheet[work].write(r, c, b_qty, text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, r_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, s_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, i_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, o_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, p_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, po_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, a_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, e_qty , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, cost , text_right_bold1)
                    c += 1
                    worksheet[work].write(r, c, total_cost , text_right_bold1)
                    r += 1
            work+=1

        
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=dev.stock.inventory&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, filename),
                'target': 'new',
            }
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
