# -*- coding: utf-8 -*-

{
    'name': "PromptPayQR Payment Acquirer",
    'summary': 'PromptPayQR Payment Acquirer: implementationa',
    'description': """Transfer Payment Acquirer using PromptPay QR code format""",
    'author': "Poommitol Chaicherdkiat, Nayan Chandra Nath",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['payment', 'website_sale'],
    'data': [
        'views/promptpayqr_transfer_template.xml',
        'views/promptpayqr_view.xml',
        'data/payment_acquirer_data.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
}
