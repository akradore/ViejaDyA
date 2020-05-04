# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Website Warehouse',
        help='')
    
    route_id = fields.Many2one(
        'stock.location.route',
        'Website Location',
        help='')
    
    @api.onchange('warehouse_id')
    def get_route(self):
        """ Finds Route for changed warehouse. """        
        routes=[]
        if self.warehouse_id:
            for route in self.env['stock.location.route'].search([]):
                if self.warehouse_id in route.warehouse_ids or not route.warehouse_ids:
                    if route.pull_ids:
                        for pull_id in route.pull_ids:                                                    
                            if self.warehouse_id==pull_id.warehouse_id or pull_id.warehouse_id==False:
                                routes.append(route.id)
                    else:
                        routes.append(route.id)                
        else:
            route=self.env['stock.location.route'].search([])
            if route:
                routes.extend(route.ids)
        return {'domain':{'route_id':[('id','in',routes), ('sale_selectable','=',True)]}}
        
    @api.onchange('route_id')
    def get_warehouse(self):
        warehouses=[]
        if self.route_id and self.route_id.pull_ids:
            for pull_id in self.route_id.pull_ids:
                if not pull_id.warehouse_id:
                    warehouse=self.env['stock.warehouse'].search([])
                    if warehouse:
                        warehouses.extend(warehouse.ids)
                if pull_id.warehouse_id:
                    warehouses.append(pull_id.warehouse_id.id)
            if self.route_id.warehouse_ids:
                warehouses.extend(self.route_id.warehouse_ids.ids)
        else:
            warehouse=self.env['stock.warehouse'].search([])
            if warehouse:
                warehouses.extend(warehouse.ids)
        return {'domain':{'warehouse_id':[('id','in',warehouses)]}}    
    
    @api.model
    def get_values(self):
        res = super(ResConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            warehouse_id=int(ICPSudo.get_param('website_warehouse_stock_ept.warehouse_id', default=False)),
            route_id=int(ICPSudo.get_param('website_warehouse_stock_ept.route_id', default=False)),
        )
        return res
    
    @api.multi
    def set_values(self):
        super(ResConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("website_warehouse_stock_ept.warehouse_id", self.warehouse_id.id)
        ICPSudo.set_param("website_warehouse_stock_ept.route_id", self.route_id.id)
    
            