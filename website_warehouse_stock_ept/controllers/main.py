# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.http import request
from odoo.tools.pycompat import izip
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):

    def get_attribute_value_ids(self, product):        
        res = super(WebsiteSale, self).get_attribute_value_ids(product)        
        warehouse_id = request.env['ir.config_parameter'].sudo().get_param('website_warehouse_stock_ept.warehouse_id')        
        if warehouse_id:
            variant_ids = [r[0] for r in res]                               
            for r, variant in izip(res, request.env['product.product'].sudo().browse(variant_ids)):
                variant.env.context=dict(variant.env.context)
                variant.env.context.update({'warehouse':int(warehouse_id)})
                res1=variant._compute_quantities_dict(False,False,False)                
                for r in res[0]:
                    if type(r) is dict and 'virtual_available' in r.keys():
                        r.update({'virtual_available': res1[variant.id]['virtual_available']})        
        return res