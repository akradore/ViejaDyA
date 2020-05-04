# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api
  
class MrpBomLine(models.Model):
    _inherit='mrp.bom.line'
      
    product_cost = fields.Float("Cost",compute='get_product_cost')
    product_total_cost = fields.Float("Total Cost",compute='get_product_total_cost')
  
    @api.one
    @api.depends('product_id')
    def get_product_cost(self):         
        if self.product_id:
            self.product_cost = self.product_id.standard_price    

    @api.one
    @api.depends('product_qty','product_cost')
    def get_product_total_cost(self):         
        if self.product_id and self.product_qty and self.product_cost:
                self.product_total_cost = self.product_qty * self.product_cost
    
    
class MrpBom(models.Model):
    _inherit='mrp.bom'  
    
    pro_img = fields.Binary(related = 'product_tmpl_id.image_medium') 
            
    @api.one
    @api.depends('bom_line_ids')            
    def _get_total_cost_bom(self):        
        product_cost = 0 
        if self.bom_line_ids:            
            for rec in self.bom_line_ids:
                product_cost += rec.product_total_cost        
        self.total_bom_cost = product_cost                
    total_bom_cost = fields.Float("Total BoM Cost",compute ='_get_total_cost_bom')    
                
                
class ProductTemplate(models.Model):
    _inherit ='product.template'

    def _get_product_cost_bom(self): 
        
        if self.bom_count > 0 :
            total_cost_bom = 0
             
            for record in self.bom_ids:                
                if record.total_bom_cost :
                    total_cost_bom += record.total_bom_cost    
                    
            self.cost_incl_bom = total_cost_bom
    
    cost_incl_bom = fields.Monetary("Final BOM Cost",compute='_get_product_cost_bom')       