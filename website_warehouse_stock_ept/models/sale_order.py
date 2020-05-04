# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None, **kwargs):        
        res=super(SaleOrder,self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        for line in self.order_line:
            if line.product_id.type == 'product' and line.product_id.inventory_availability in ['always', 'threshold']:
                cart_qty = sum(self.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
                warehouse_id = self.env['ir.config_parameter'].sudo().get_param('website_warehouse_stock_ept.warehouse_id')    
                if cart_qty > line.product_id.with_context(warehouse=int(warehouse_id)).virtual_available if warehouse_id  else line.product_id.virtual_available and (line_id == line.id):
                    qty = (line.product_id.with_context(warehouse=int(warehouse_id)).virtual_available if warehouse_id else line.product_id.virtual_available) - cart_qty                    
                    new_val = super(SaleOrder, self)._cart_update(line.product_id.id, line.id, qty, 0, **kwargs)  
        route_id=self.env['ir.config_parameter'].sudo().get_param('website_warehouse_stock_ept.route_id')
        line_id=self.env['sale.order.line'].sudo().search([('id','=',res['line_id'])])
        if route_id:
            line_id.write({'route_id':route_id})
        return res
    