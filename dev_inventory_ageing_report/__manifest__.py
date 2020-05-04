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
    'name': 'Stock Aging Report',
    'version': '11.0.1.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Stock Aging Report by Compnay, Warehoouse, Location, Product Category and Product',
    'description': """
        Apps will print Stock Aging Report by Compnay, Warehoouse, Location, Product Category and Product.
    """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    'depends': ['base','purchase','stock','mrp','account','sale_stock',],
    'data': [
        'wizard/inventory_wizard_view.xml',
        'report/stock_inv_ageing_report.xml',
        'report/report_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application':True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
