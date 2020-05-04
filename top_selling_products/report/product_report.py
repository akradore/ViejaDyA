# -*- coding: utf-8 -*-
import time
from odoo import api, models

class TopSellingReport(models.AbstractModel):
    _name = 'report.top_selling_products.product_report'

    @api.model
    def get_report_values(self, docids, data=None):
        Report = self.env['ir.actions.report']._get_report_from_name('top_selling_products.product_report')
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        product_records = {}
        sorted_product_records = []
        domain = [
            ('state', '=', 'done'),
            ('picking_type_id.code', '=', 'outgoing'),
            ('date', '>=', docs.start_date),
            ('date', '<=', docs.end_date),
        ]
        if docs.company_id:
            domain += [('company_id', 'in', docs.company_id.ids)]
        if docs.warehouse_id:
            domain += [('picking_type_id.warehouse_id', 'in', docs.warehouse_id.ids)]

        move_ids = self.env['stock.move'].search(domain)

        for move in move_ids:
            if docs.report_group_by == "template":
                if move.product_id.product_tmpl_id not in product_records:
                    product_records.update({move.product_id.product_tmpl_id: 0})
                product_records[move.product_id.product_tmpl_id] += move.product_uom_qty
            else:
                if move.product_id not in product_records:
                    product_records.update({move.product_id: 0})
                product_records[move.product_id] += move.product_uom_qty

        for product_id, product_uom_qty in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True)[:docs.display_product]:
            sorted_product_records.append({'name': product_id.display_name, 'qty': int(product_uom_qty)})
        return {
            'docs': docs,
            'data': data,
            'doc_model': Report.model,
            'time': time,
            'products': sorted_product_records,
            'doc_ids': self.ids,
        }
