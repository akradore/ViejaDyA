# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductSellingDetail(models.TransientModel):
    _name = "product.selling.detail"

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    display_product = fields.Integer(string='Top * Products', help="Print Number of top selling products in report")
    company_id = fields.Many2one("res.company", string="Company", default=_default_company, required=True, help="Check Top Selling Product from selected Company only. if its blank it checks in all Company")
    warehouse_id = fields.Many2many("stock.warehouse", string="Warehouse", help="Check Top Selling Product from selected Warehouse only. if its blank it checks in all Warehouse")
    report_group_by = fields.Selection([('template', 'By Template'), ('product', 'By Product')], required=True, default='template', String="Group")

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.warehouse_id = ''

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        domain = {}
        domain['warehouse_id'] = []
        if self.company_id:
            domain['warehouse_id'] = [('company_id', 'in', self.company_id.ids)]
        return {'domain': domain}

    @api.multi
    def print_top_selling_product_report(self, rer):
        data = {}
        data['form'] = (self.read(['start_date', 'end_date', 'display_product', 'company_id', 'warehouse_id'])[0])
        return self.env.ref('top_selling_products.action_product_reports').report_action(self, data=data)
