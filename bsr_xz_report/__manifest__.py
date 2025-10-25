{
    'name': 'POS X/Z Reports',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Adds X and Z reports to the Point of Sale',
    'description': """
        This module adds X and Z reports to the Point of Sale.
    """,
    'author': 'BSR',
    'website': '',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'report/paper_format.xml',
        'report/pos_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_qweb': [
            'bsr_xz_report/static/src/xml/pos_xz_report_templates.xml',
        ],
        'point_of_sale.assets': [
            'bsr_xz_report/static/src/js/pos_xz_report.js',
        ],
    },
}
