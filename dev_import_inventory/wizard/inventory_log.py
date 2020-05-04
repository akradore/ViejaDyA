# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

from odoo import api, fields, models, _


class inventory_log(models.TransientModel):
    _name = "inventory.log"


    name = fields.Text(string='Logs')
    
    
            

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    
