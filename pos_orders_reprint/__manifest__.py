# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Orders Reprint",
    "version" : "11.0.0.2",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale','pos_orders_list'],
    "author": "BrowseInfo",
    'summary': 'This apps helps to reprint existing POS Orders from Order list',
    "description": """

    Purpose :-
    POS Orders Reprint
    POS reprint
    POS order reprint
    Reprint receipt from POS
    POS receipt reprint
    POS reprint receipt
    reprint pos orders
    Receipt print from POS
    POS order print
    POS order receipt print
    POS receipt print
    Receipt reprint from POS
    POS all order list
    POS show all order list
    
    """,
    "website" : "www.browseinfo.in",
    'price': '5',
    'currency': "EUR",
    "data": [
        'views/custom_pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_orders_reprint.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/32cGBhstV14',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
