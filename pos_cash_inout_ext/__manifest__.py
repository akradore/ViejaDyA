# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'POS Cash In-Out Extension',
    'version': '1.0',
    'category': 'Point of Sale',
    'description': """
This module allows user to put money in and take money out from frontend in POS.
""",
    'summary': 'This module allows user to put money in and take money out from frontend in POS.',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 38.00,
    'currency': 'EUR',
    'depends': ['base', 'point_of_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_cash_inout.xml',
        'views/point_of_sale.xml',
        'views/cash_inout_menu.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: