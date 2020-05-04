# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name' : 'Add Sale Order Line In Batch',
    'version': '11.0.0.1',
    'summary': 'Quick Add Many Products In Sale Order',
    'category': 'Sale',
    'description': """User can add multiple sale order line at a time""",
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'depends': ['product', 'sale'],
    'data': [
             'wizard/select_products_wizard_view.xml',
             'views/sale_views.xml',
             'security/ir.model.access.csv'
            ],
    'images': ['static/description/banner.gif'],
    'price': 14.00,
    'currency': 'EUR',
    'qweb': [],
}
