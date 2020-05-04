# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools

class Website(models.Model):
    _inherit = 'website'
    
    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        res=super(Website,self)._prepare_sale_order_values(partner,pricelist)
        warehouse_id = self.env['ir.config_parameter'].sudo().get_param('website_warehouse_stock_ept.warehouse_id')
        if warehouse_id:
            res.update({'warehouse_id':int(warehouse_id)})
        return res