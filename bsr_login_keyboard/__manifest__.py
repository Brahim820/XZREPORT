{
    'name': 'BSR Login Keyboard',
    'version': '15.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Adds a keyboard to the login interface',
    'description': """
        This module adds a keyboard to the login interface of Odoo 15.
    """,
    'author': 'BSR',
    'website': 'https://www.bsr.com',
    'depends': ['web'],
    'data': [
        'views/web_login_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'bsr_login_keyboard/static/src/js/login_keyboard.js',
        ],
        'web.assets_qweb': [
            'bsr_login_keyboard/static/src/xml/login_keyboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
