# -*- coding: utf-8 -*-
{
    'name' : 'Split Quotation, Sales Order And RFQ, Purchase Order',
    'author' : 'Softhealer Technologies',
    'website': 'http://www.softhealer.com',
    'category': 'Sales',
    'description': """This module useful to split quotation and RFQ into multiple quotations and RFQs""",    
    'version':'11.0.1',
    'depends' : ['base','sale','purchase','sale_management'],
    'application' : True,
    'data' : ['views/split_view.xml',
              'security/split_quo_security.xml',
            ],            
    'images': ['static/description/background.png',],              
    'auto_install':False,
    'installable' : True,
    'license': 'LGPL-3',
    "price": 22,
    "currency": "EUR"    
}
