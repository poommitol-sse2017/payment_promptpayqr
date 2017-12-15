# -*- coding: utf-8 -*-

{
    'name': "PromptPayQR Payment Acquirer",
    'summary': 'PromptPayQR Payment Acquirer: implementation',
    'description': """Transfer Payment Acquirer using PromptPay QR code format""
    <img src="/payment_promptpayqr/static/src/img/transfer_icon.png"/>",
    'author': "Poommitol Chaicherdkiat, Nayan Chandra Nath",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['payment', 'website_sale'],
    'data': [
        'views/promptpayqr_transfer_template.xml',
        'views/promptpayqr_view.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
