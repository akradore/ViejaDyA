# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

{
    'name': 'Stock Inventory Real Time Report(PDF/XLS)',
    'version': '11.0.1.2',
    'category': 'Stock',
    'sequence': 1,
    'description': """
        This module will help to print stock Inventory PDF and XLS Report.
    """,
    'summary':"""print Stock Inventory PDF and XLS Report""",
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    'images': [],
    'depends': ['sale_management','sale_stock','purchase','mrp'],
    'data': [
        'wizard/dev_stock_inventory_views.xml',
        'report/stock_inventory_template.xml',
        'report/dev_stock_inventory_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application':True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



