# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class ProductMultiSelection(models.TransientModel):
    _name = 'product.multiselect'
    _desciption = 'Select Products Wizard'

    product_ids = fields.Many2many('product.product')

    @api.multi
    def set_products(self):
        if self.product_ids:
            return {
                'name': _('Set Product Qty'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'select.products',
                'target': 'new',
                'context': {'selected': self.product_ids.ids, 
                            'sale_id': self._context.get('active_id', False)}
            }


class ProductQty(models.TransientModel):
    _name = 'product.qty'
    _desciption = 'Product Qty Wizard'

    product_id = fields.Many2one('product.product', string="Products")
    qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), required=True, default=1.0)
    select_pid = fields.Many2one('select.products')


class SelectProducts(models.TransientModel):
    _name = 'select.products'
    _desciption = 'Set Qty and Products Wizard'

    product_ids = fields.One2many('product.qty', 'select_pid')

    @api.model
    def default_get(self, fields):
        res = super(SelectProducts, self).default_get(fields)
        selected_products = self._context.get('selected')
        values = []
        if selected_products:
            for product in selected_products:
                result = {'product_id': product, 'qty': 1.0}
                values.append((0, 0, result))
            res['product_ids'] = values
        return res

    @api.multi
    def select_products(self):
        if self._context.get('sale_id') and self.product_ids:
            order_id = self.env['sale.order'].browse(
                self._context.get('sale_id', False))
            for product in self.product_ids:
                line_values = {
                    'product_id': product.product_id.id,
                    'order_id': order_id.id,
                }
                sale_line = self.env['sale.order.line'].new(line_values)
                sale_line.product_id_change()
                sale_line.product_uom_change()
                sale_line._onchange_discount()
                line_values = sale_line._convert_to_write({name: sale_line[name] for name in sale_line._cache})
                line_values['product_uom_qty'] = product.qty
                order_id.write({'order_line': [(0, 0, line_values)]})
