# See LICENSE file for full copyright and licensing details.

{
    # Module Info.
    "name": "SCS Product Image Export",
    "version": "11.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "sequence": 1,
    "summary": """
        Images Export Option, Export Product Images, Product Images Zip,
        Multiple Products Images Export at Once.
    """,
    "description": """
        Images Export Option, Export Product Images, Product Images Zip,
        Multiple Products Images Export at Once.
    """,

    # Author
    "author": 'Serpent Consulting Services Pvt. Ltd.',
    "website": "http://www.serpentcs.com",
    "maintainer": 'Serpent Consulting Services Pvt. Ltd.',

    # Dependencies
    'depends': ['product'],

    # Data
    'data': [
        'wizard/wiz_export_image_view.xml',
    ],

    # Technical
    'installable': True,
    'auto_install': False,
    'price': 49,
    'currency': 'EUR',
}
