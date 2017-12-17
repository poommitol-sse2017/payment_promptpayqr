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
        
        # Valid Class 
        self.promptpay_national_id = '0123456789012'
        self.promptpay_phone_id = '0123456789'
        self.valid_amount = 0.01
       
        # Invalid class (Borderline and Equivalent analysis)
        self.promptpay_tooshort_phone_id = '012345678'
        self.promptpay_toolong_phone_id = '01234567890' # equivalent to too_short_national_id
        self.promptpay_toolong_national_id = '01234567890123'
        self.invalid_amount = 0.00

        # Expected valid class result
        self.expected_national_qr_string = '00020101021129370016A000000677010111021301234567890125802TH54040.01530376463041898'
        self.expected_phone_qr_string = '00020101021129370016A000000677010111011300661234567895802TH54040.01530376463047e9e'
       
        # Group every test case into array
        self.expected_valid_result = [{'id':self.promptpay_national_id, 'qrstring':self.expected_national_qr_string, 'ref':'SO9999','amount': self.valid_amount},
                                {'id':self.promptpay_phone_id, 'qrstring':self.expected_phone_qr_string,'ref':'SO0000', 'amount': self.valid_amount}]
        
        self.expected_invalid_result = [{'id':self.promptpay_tooshort_phone_id,'ref':'SO9998','amount': self.valid_amount },
                                {'id':self.promptpay_toolong_phone_id, 'ref':'SO9997','amount': self.valid_amount},
                                {'id':self.promptpay_toolong_national_id, 'ref':'SO9996','amount': self.valid_amount},
                                {'id':self.promptpay_national_id, 'ref':'SO9995','amount': self.invalid_amount} #Invalid amount test
]
        self.expected_invalid_amount_result = {'id':self.promptpay_national_id, 'ref':'SO9995','amount': self.invalid_amount}

class PromptpayForm(PromptpayCommon):

    # Test for EMVco Merchant string format 
    def test_10_qr_string(self):
        # Test for valid class
        for test_case in self.expected_valid_result:
            # Set PromptPay ID
            self.promptpay.write({'promptpay_id': test_case['id'], 'promptpay_account_name': 'AnonymousThais'})
            
            # create tx
            tx = self.env['payment.transaction'].create({
                'amount': test_case['amount'],
                'acquirer_id': self.promptpay.id,
                'currency_id': self.currency_us.id,
                'reference': test_case['ref'],
                'partner_name': 'Norbert Buyer',
                'partner_country_id': self.country_france.id})         
            self.assertEqual(tx._get_promptpayqr_str(test_case['id'],test_case['amount']), test_case['qrstring'], 'promptpay: wrong qrcode format after receiving a valid pending notification')
       
        # Test for invalid PromptPay ID class
        for test_case in self.expected_invalid_result:
            # create tx
            tx = self.env['payment.transaction'].create({
                'amount': test_case['amount'],
                'acquirer_id': self.promptpay.id,
                'currency_id': self.currency_us.id,
                'reference': test_case['ref'],
                'partner_name': 'Norbert Buyer',
                'partner_country_id': self.country_france.id})        
            self.assertFalse(tx._get_promptpayqr_str(test_case['id'],test_case['amount']),'promptpay: invalid promptpay id can generate QRcode')
        
    def test_11_promptpay_form_management(self):
        
        # be sure not to do stupid things
        self.assertEqual(self.promptpay.environment, 'test', 'test without test environment')
        
        # Test for valid class
        for test_case in self.expected_valid_result:
            
            # Set PromptPay ID
            self.promptpay.write({'promptpay_id': test_case['id'], 'promptpay_account_name': 'AnonymousThais'})
            
            # typical data posted by promptpay after client has selected payment method, then click pay button
            promptpay_post_data = {
                'amount': test_case['amount'],
                'currency': u'USD',
                'reference': test_case['ref'],
                'return_url': u'/shop/payment/validate'
            }
            
            # should raise error about unknown tx
            with self.assertRaises(ValidationError):
                self.env['payment.transaction'].form_feedback(promptpay_post_data, 'promptpayqr')
            
            # create tx
            tx = self.env['payment.transaction'].create({
                'amount': test_case['amount'],
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
        
         # Test for invalid PromptPay ID class
        for test_case in self.expected_invalid_result:
            
            # Set PromptPay ID
            self.promptpay.write({'promptpay_id': test_case['id'], 'promptpay_account_name': 'AnonymousThais'})
            
            # typical data posted by promptpay after client has selected payment method, then click pay button
            promptpay_post_data = {
                'amount': test_case['amount'],
                'currency': u'USD',
                'reference': test_case['ref'],
                'return_url': u'/shop/payment/validate'
            }
            
            # should raise error about unknown tx
            with self.assertRaises(ValidationError):
                self.env['payment.transaction'].form_feedback(promptpay_post_data, 'promptpayqr')
            
            # create tx
            tx = self.env['payment.transaction'].create({
                'amount': test_case['amount'],
                'acquirer_id': self.promptpay.id,
                'currency_id': self.currency_us.id,
                'reference': test_case['ref'],
                'partner_name': 'Norbert Buyer',
                'partner_country_id': self.country_france.id})

            # should raise error because invalid QR code
            with self.assertRaises(ValidationError):
                tx.form_feedback(promptpay_post_data, 'promptpayqr')
            
    
            
            
            