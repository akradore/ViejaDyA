# -*- coding: utf-8 -*-
{
    'name': 'Top Selling Products',
    'summary': "Top / Most / Best Selling Products from Warehouse",
    'description': """Top / Most / Best Selling Products from Warehouse""",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    "support": "ipredictitsolutions@gmail.com",

    'category': 'Warehouse',
    'version': '11.0.0.1.0',
    'depends': ['stock'],
    'data': [
        'report/product_template_view.xml',
        'report/product_report_action.xml',
        'wizard/top_selling_product_view.xml',
        'views/top_selling_menu_view.xml',
    ],

    'license': "OPL-1",
    'price': 19,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/main.png'],
}
