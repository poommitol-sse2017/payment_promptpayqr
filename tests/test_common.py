# -*- coding: utf-8 -*-

from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.addons.payment_promptpayqr.controllers.controllers import PromptpayController
from odoo.tools import mute_logger

from lxml import objectify
import urlparse
import logging
_logger = logging.getLogger(__name__)

class PromptpayCommon(PaymentAcquirerCommon):

    # general setup method for data preparation
    def setUp(self):
        super(PromptpayCommon, self).setUp()
        self.currency_us = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)   
        self.promptpay = self.env.ref('payment.payment_acquirer_promptpayqr')
        self.promptpay_national_id = '0123456789012'
        self.promptpay_phone_id = '0123456789'
        self.promptpay_account_id = '012345678901234'
        
        self.promptpay_tooshort_id = '01234578'
        self.promptpay_toolong_id = '0123456789012345'
        
        
        self.amount = '10.0'
        self.expected_national_qr_string = '00020101021129370016A000000677010111021301234567890125802TH540410.05303764630416f'
        self.expected_phone_qr_string = '00020101021129370016A000000677010111011300661234567895802TH540410.0530376463046769'
        self.expected_account_qr_string = '00020101021129390016A00000067701011103150123456789012345802TH540410.0530376463041c13'
        
        self.expected_result = [{'id':self.promptpay_national_id, 'qrstring':self.expected_national_qr_string, 'ref':'SO9999'},
                                {'id':self.promptpay_phone_id, 'qrstring':self.expected_phone_qr_string,'ref':'SO0000'},
                                {'id':self.promptpay_account_id, 'qrstring':self.expected_account_qr_string,'ref':'SO1010'}]
        self.expected_bad_result = [{'id':self.promptpay_tooshort_id, 'qrstring':self.expected_national_qr_string, 'ref':'SO9999'},
                                {'id':self.promptpay_toolong_id, 'qrstring':self.expected_phone_qr_string,'ref':'SO0000'}]
        

class PromptpayForm(PromptpayCommon):

    # Test for EMVco Merchant string format 
    def test_10_qr_string(self):
        for test_case in self.expected_result:
            # Set PromptPay ID
            self.promptpay.write({'promptpay_id': test_case['id'], 'promptpay_account_name': 'AnonymousThais'})
            
            # create tx
            tx = self.env['payment.transaction'].create({
                'amount': '10.0',
                'acquirer_id': self.promptpay.id,
                'currency_id': self.currency_us.id,
                'reference': test_case['ref'],
                'partner_name': 'Norbert Buyer',
                'partner_country_id': self.country_france.id})         
            self.assertEqual(tx._get_promptpayqr_str(test_case['id'],self.amount), test_case['qrstring'], 'promptpay: wrong qrcode format after receiving a valid pending notification')
        
        for test_case in self.expected_bad_result:
            self.assertFalse(tx._get_promptpayqr_str(test_case['id'],self.amount),'promptpay: invalid promptpay id can generate QRcode')


    def test_11_promptpay_form_management(self):
        
        # be sure not to do stupid things
        self.assertEqual(self.promptpay.environment, 'test', 'test without test environment')
        
        for test_case in self.expected_result:
            
            # Set PromptPay ID
            self.promptpay.write({'promptpay_id': test_case['id'], 'promptpay_account_name': 'AnonymousThais'})
            
            # typical data posted by promptpay after client has selected payment method, then click pay button
            promptpay_post_data = {
                'amount': 10.0,
                'currency': u'USD',
                'reference': test_case['ref'],
                'return_url': u'/shop/payment/validate'
            }
            
            # should raise error about unknown tx
            with self.assertRaises(ValidationError):
                self.env['payment.transaction'].form_feedback(promptpay_post_data, 'promptpayqr')
            
            # create tx
            tx = self.env['payment.transaction'].create({
                'amount': '10.0',
                'acquirer_id': self.promptpay.id,
                'currency_id': self.currency_us.id,
                'reference': test_case['ref'],
                'partner_name': 'Norbert Buyer',
                'partner_country_id': self.country_france.id})

            # validate it
            tx.form_feedback(promptpay_post_data, 'promptpayqr')
            
            # check the state after validation
            self.assertEqual(tx.state, 'pending', 'promptpay: wrong state after receiving a valid pending notification')  
            
            # check the correction of EMVco QR code string 
            self.assertEqual(tx.promptpay_qrcode, test_case['qrstring'], 'promptpay: wrong qrcode format after receiving a valid pending notification')
        