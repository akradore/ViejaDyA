# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # App information
   
    'name': 'Display Only Specific Warehouse Stock at Odoo Website',
    'version': '11.0',
    'category': 'Website',
    'license': 'OPL-1',
    'summary': """Assign the dedicated warehouse to a particular Website so sales from the other channels do not impact to run out of stock for your eCommerce customers.""",
    
    # Dependencies
    
    'depends': ['website_sale_stock'],
    
    # Views
    
    'data': [
        'views/res_config_setting.xml',
    ],
       
    # Odoo Store Specific
    
   'images': ['static/description/Display-Only-Specific-Warehouse-Cover.jpg'],
    
    # Author

    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
       
       
    # Technical 
    
    'installable': True,
    'currency': 'EUR',
    'price': 49.00,
    'live_test_url':'http://www.emiprotechnologies.com/free-trial?app=website-warehouse-stock-ept&version=11',
    'auto_install': False,
    'application': True,
}
