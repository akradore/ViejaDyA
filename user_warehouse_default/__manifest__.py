# -*- coding: utf-8 -*-
{
    "name": "User Default Warehouse",
    "version": "11.0.1.0.1",
    "category": "Warehouse",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/11.0/user-default-warehouse-283",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "sale_stock"
    ],
    "data": [
        "views/res_users.xml",
        "data/data.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to automatically assign a current user warehouse in sales orders",
    "description": """
    The tool let you simplify salespersons work, if your company has several warehouses

    This tool is a limited version of the module <a href='https://apps.odoo.com/apps/modules/11.0/product_stock_balance/'>Stocks by Locations</a>
    The tool let users changing default warehouse in their preferences
    Odoo administrators may define salespersons' warehouse while configuring users
    When a salesperson generates a new quotation his/her warehouse is set by default
    If a salesperson is changed, a quotation warehouse is updated correspondingly 
    Users may change their default warehouse in preferences
    Sale order warehouse is updated according to a current salesperson
    Odoo admins may update a default warehouse in user settings
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "19.0",
    "currency": "EUR",
}