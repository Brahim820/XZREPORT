{
    'name': 'Treasury Forecast',
    'version': '15.0.1.0.0',
    'summary': 'Treasury Forecast and Cash Flow Management',
    'author': 'BSR',
    'website': '',
    'license': 'OPL-1',
    'category': 'Accounting',
    'depends': [
        'account',
        'mail',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/treasury_forecast_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bsr_treasury_forecast/static/src/js/treasury_chart_widget.js',
        ],
        'web.assets_qweb': [
            'bsr_treasury_forecast/static/src/xml/treasury_chart_templates.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
}
