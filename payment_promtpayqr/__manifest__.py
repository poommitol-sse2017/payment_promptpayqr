# -*- coding: utf-8 -*-

{
    'name': "PromtpayQR Payment Acquirer",
    'summary': 'PromtpayQR Payment Acquirer: implementation',
    'description': """Transfer Payment Acquirer using Promtpay QR code format""",
    'author': "Poommitol Chaicherdkiat, Nayan Chandra Nath",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['payment'],
    'data': [
        'views/promtpayqr_transfer_template.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'auto_install': True,
}