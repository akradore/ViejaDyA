# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    'name': 'BOM Cost Price',
    'author' : 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',    
    'version': '11.0.2',
    "category": "Manufacturing",
    'summary': 'MRP BOM Product Cost Price',
    'description': """
    This module used to get total cost of manufactuing product.
    This module used to get BoM product image in BoM form and BoM cost report.    
    """,
    'depends': ['mrp'],
    'data': [
        'views/product_template.xml',
        'report/sh_BoM_structure_inherit_template.xml',
    ],
    'images': ['static/description/background.png',],              
    'auto_install':False,
    'installable' : True,
    'application': True,    
    "price": 13,
    "currency": "EUR"        
}
