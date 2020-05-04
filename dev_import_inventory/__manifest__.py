# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

{
    'name': 'Import Inventory adjustment from  CSV/XLS',
    'version': '1.1',
    'category': 'Generic Modules/Warehouse',
    'sequence':1,
    'summary': 'odoo Apps will help to Import Inventory adjustment in CSV or XLS format',
    'description': """
        odoo Apps will help to Import Inventory adjustment in CSV or XLS format

		
		import Inventory , import Inventory adjustment line, import Inventory adjustment by csv, import Inventory adjustment by xls, import Inventory adjustment , Inventory adjustment, Inventory adjustment Csv, Inventory adjustment by XLS
Import Inventory adjustment from CSV/XLS
Import inventory from csv
Import inventory from XLS
Import inventory from excel
Import inventory adjustment from csv
Import inventory adjustment from xls
How can import inventory repor
How can import inventory adjustment from CSV
How can import inventory adjustment from XLS
How can import inventory adjustment from excel
Import inventory
import csv, xlsx and xls file to create Inventory adjustments.
import inventory in Inventory module
import the inventory data from file.
Easily create inventory adjustment from excel 
Easily create inventory adjustment from csv
Easily create inventory adjustment from xls
Odoo Import inventory from CSV 
Odoo Import inventory from excel
Odoo Import inventory from xls
Generate inventory adjustment for opening stock.
Import of Inventory using csv / xls with different scenarios
Import inventory using csv/xls with different ways
Import Serial/lot no. with expiry date using csv / xls
Import location using csv / xls
Import inventory adjust line
Import Inventory adjust line easily from excel/csv to odoo		
		
		
            """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'depends': ['sale','sale_stock'],
    'data': [
        'wizard/import_inventory_lines_view.xml',
        'views/inventory_view.xml',
        'wizard/inventory_log_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':20.0,
    'currency':'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
