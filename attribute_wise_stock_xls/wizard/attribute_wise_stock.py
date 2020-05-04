# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution.(<https://tidyway.in/>)

import base64
import xlwt
from io import BytesIO

from odoo import models, api, fields, _
from odoo.exceptions import Warning
from operator import itemgetter
from itertools import groupby
from . import style_format


class attribute_wise_stock(models.TransientModel):
    _name = 'attribute.wise.stock'

    location_ids = fields.Many2one('stock.location', string='Location', domain=[('usage', '=', 'internal')])
    product_category_ids = fields.Many2many('product.category', string='Product Category')
    product_template_ids = fields.Many2many('product.template', string='Product Templates')

    @api.onchange('product_category_ids')
    def onchange_product_category_ids(self):
        product_categories_ids = [z.id for z in self.product_category_ids]
        search_args = product_categories_ids and [('categ_id', 'in',product_categories_ids)] or []

        return {
                'domain': {
                           'product_template_ids': [('id','in',[x.id for x in self.env['product.template'].search(search_args)] )]
                           }
                }

    def _fetch_data(self, vals):
        """
        Login to group by products
        """
        add, new_value,total_qty = True, {},0.0
        for data in vals:
            if add:
                new_value.update(data)
                add = False
            total_qty += data.get('qty',0.0) or 0.0
        new_value['total_qty'] = total_qty
        return new_value

    def _template_wise_group(self, template_id, vals):
        final_dict = {
                      'name': self.env['product.template'].browse(template_id).name
                      }
        for data in vals:
            final_dict.update(
                              {
                               data.get('attribute','other') or 'other':data.get('total_qty',0.0) or 0.0 
                               }
                              )
        return final_dict

    @api.multi
    def xls_data(self):
        """
        -Process
            - Fetch all locations and product templates
            - Make clear header with attributes
            - Find all products stock from quants
            - Merge those products with location
            - Group by with product template and make all products in one line(attribute wise)
            - {
                'template_id': {
                                'att1': qty
                                'att2': qty
                                ...
                                }
                ...
                }
            - Write into XLS
        """
        quant_obj = self.env['stock.quant']
        location_ids = [x.id for x in self.location_ids] or [y.id for y in self.env['stock.location'].search([('usage','=','internal')])] or []

        wizard_templates_ids = [p.id for p in self.product_template_ids]
        product_categories_ids = [z.id for z in self.product_category_ids]
        #IF categories selected defaults withouts templates then domain will be set base on categories  
        search_args = product_categories_ids and [('categ_id', 'in',product_categories_ids)] or []
        product_templates_ids = wizard_templates_ids or [q.id for q in self.env['product.template'].search(search_args)] or []

        if not (product_templates_ids or location_ids):
            raise Warning(_('There is no any location or products templates define in your system, please check your system.'))

        products_ids = self.env['product.product'].search([('product_tmpl_id', 'in', product_templates_ids)])

        Header = ['name']
        for product in products_ids:
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            insert_value = variant.strip()
            if insert_value and (insert_value not in Header):
                Header.append(insert_value)
        Header.append('other')

        search_args = [('location_id', 'in', location_ids),('product_id','in',[c.id for c in products_ids])]
        all_quants = quant_obj.search(search_args)
        raw_list = []
        for quant in all_quants:
            variant = ", ".join([v.name for v in quant.product_id.attribute_value_ids])
            raw_list.append({
                             'product_id': quant.product_id.id,
                             'template_id': quant.product_id.product_tmpl_id.id,
                             'qty': quant.quantity,
                             'attribute': variant.strip() or 'other',
                             #variant.strip() or 'other': quant.qty,
                             })

        #records by products
        sort_by_products = sorted(raw_list, key=itemgetter('product_id'))
        records_by_products = dict((k, [v for v in itr]) for k, itr in groupby(sort_by_products, itemgetter('product_id')))

        group_by_products = []
        for product,vals in  records_by_products.items():
            group_by_products.append(self._fetch_data(vals))

        #records by product templates
        sort_by_templates = sorted(group_by_products, key=itemgetter('template_id'))
        records_by_templates = dict((k, [v for v in itr]) for k, itr in groupby(sort_by_templates, itemgetter('template_id')))

        #Group by product templates
        final_result = []
        for template,t_vals in records_by_templates.items():
            final_result.append(self._template_wise_group(template, t_vals))

        get_file = self._xls_write(Header, final_result)
        return get_file

    def _xls_write(self, Header, xls_data):

        wb1 = xlwt.Workbook()
        ws1 = wb1.add_sheet('Current Stock')

        header_para_style = style_format.font_style(position='center', bold=1,border=1, fontos='black', font_height=150, color='yellow')
        header_para_style_total = style_format.font_style(position='center', bold=1,border=1, fontos='black', font_height=200, color='yellow')
        header_para_style_total_no_color = style_format.font_style(position='center', bold=1,border=1, fontos='black', font_height=200)
        para_style = style_format.font_style(position='center', fontos='black', font_height=200)
        #para_style_left = style_format.font_style(position='left', fontos='black', font_height=200, bold=1)

        # Headers
        raw_start_h = raw_end_h = 0
        ws1.write_merge(0, 0, 0, 0, 'name', header_para_style)
        Header.remove('name')
        header_position = {
                           'name': [0,0],
                           }

        ws1.row(0).height = 256*3
        ws1.col(0).width = 6000
        for part in Header:
            raw_start_h += 1
            raw_end_h += 1
            header_position[part] = [raw_start_h, raw_end_h]
            ws1.write_merge(0, 0, raw_start_h, raw_end_h, part, header_para_style)

        final_raw_start_h = raw_start_h+1
        final_raw_end_h = raw_end_h+1
        ws1.write_merge(0, 0, final_raw_start_h, final_raw_end_h, 'Total', header_para_style_total)
        header_position['Total'] = [final_raw_start_h,final_raw_end_h]

        #Used horizontal total
        total_positions = {}
        for r in range(1, final_raw_start_h+1):
            total_positions.update({r:[]})

        raw_start = raw_end = 0
        for line in xls_data:
            raw_start += 1
            raw_end += 1
            line.update(Total=self._give_total_dict(line))
            for key,position in header_position.items():
                style = para_style
                if key == 'Total': style = header_para_style_total_no_color
                if line.get(key):
                    ws1.write_merge(raw_start, raw_end, position[0], position[1], line[key], style)
                    #Used horizontal total
                    if key != 'name': total_positions.get(position[0]).append(line[key])
                else:
                    ws1.write_merge(raw_start, raw_end, position[0], position[1], '-', style)

        #Used horizontal total
        final_raw_start = raw_start+1
        final_raw_end = raw_end+1
        ws1.write_merge(final_raw_start, final_raw_end, 0, 0, 'Total', header_para_style_total)
        for pos,total in total_positions.items():
            ws1.write_merge(final_raw_start, final_raw_end, pos, pos, sum(total), header_para_style_total)

        stream = BytesIO()
        wb1.save(stream)
        return stream.getvalue()

    def _give_total_dict(self, lines):
        total = 0.0
        for key,values in lines.items():
            if key in ('name'):
                continue
            total += values
        return total

    @api.multi
    def print_report(self):
        """
            Print report templates wise attribute stock  
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        export_obj = self.env['attribute.report.export']
        self._cr.execute(""" DELETE FROM attribute_report_export""")
        res_id = export_obj.create({
                                    'file':base64.encodestring(self.xls_data()),
                                    'fname' : "Attribute Wise Report.xls"  # str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
                                    })
        return {
             'type': 'ir.actions.act_url',
             'url': '/web/binary/download_document?model=attribute.report.export&field=file&id=%s&filename=Attribute_Wise_Report.xls'%(res_id.id),
             'target': 'new',
             }


class attribute_report_export(models.TransientModel):
    _name = "attribute.report.export"
    _description = "Finished"

    file = fields.Binary('File', readonly=True)
    fname = fields.Char('Text')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
