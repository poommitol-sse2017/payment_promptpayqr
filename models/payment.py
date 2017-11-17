# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.translate import _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PromptpayPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    provider = fields.Selection(selection_add=[('promptpayqr', 'Promptpay QR')])
    
    # property for ir.view
    promptpay_id = fields.Char('PromptPay ID', required_if_provider='promptpayqr', groups='base.group_user',
                help='The PromptPay ID is a National ID or Mobile phone Number.')
    promptpay_account_name = fields.Char('Account Name', required_if_provider='promptpayqr', groups='base.group_user',
                help='The name of bank account holder')
    promptpay_account_number = fields.Char('Account Number', required_if_provider='promptpayqr', groups='base.group_user',
                help='The account number of bank account holder')
    
    def promptpayqr_get_form_action_url(self):
        _logger.info("getting URL for promptpay")
        return '/payment/promptpay/feedback'

    def _format_transfer_data(self):
        _logger.info("Thank msg")
        company_id = self.env.user.company_id.id
        # filter only bank accounts marked as visible
        journals = self.env['account.journal'].search([('type', '=', 'bank'), ('display_on_footer', '=', True), ('company_id', '=', company_id)])
        accounts = journals.mapped('bank_account_id').name_get()
        bank_title = _('Bank Accounts') if len(accounts) > 1 else _('Bank Account')
        bank_accounts = ''.join(['<ul>'] + ['<li>%s</li>' % name for id, name in accounts] + ['</ul>'])
        post_msg = _('''<div>
            <h3>Please use the following transfer details</h3>
            <h4>%(bank_title)s</h4>
            %(bank_accounts)s
            <h4>Communication</h4>
            <p>Please use the order name as communication reference.</p>
            </div>''') % {
            'bank_title': bank_title,
            'bank_accounts': bank_accounts,
        }
        return post_msg

    @api.model
    def create(self, values):
        """ Hook in create to create a default post_msg. This is done in create
        to have access to the name and other creation values. If no post_msg
        or a void post_msg is given at creation, generate a default one. """
        if values.get('provider') == 'promptpayqr' and not values.get('post_msg'):
            values['post_msg'] = self._format_transfer_data()
        return super(PromptpayPaymentAcquirer, self).create(values)


class PromptpayPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    promptpay_qrcode = fields.Char('QRcode', default='Initial QR',required=True, help='Internal reference of the TX')
    
    @api.model
    def _promptpayqr_form_get_tx_from_data(self, data):
        reference, amount, currency_name,  = data.get('reference'), data.get('amount'), data.get('currency')
        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
       
        ### ! open for improvement !####
        # Unknow bug, the promptpay_id should be accessible by using self.acquirer_id.promptpay_id
        tx_prompt_id = self.acquirer_id.search([('promptpay_id', '!=', '')], limit=1)['promptpay_id']
        
        ########## current work here! ###############
        # TODO  implement promptpay qrcode conversion from promptpay_id and amount
        qr_string = str(reference)+','+str(tx_prompt_id)+','+str(amount)+','+str(currency_name)
        
        # for passing QRcode string to view
        tx['promptpay_qrcode'] = str(qr_string)
        return tx

    def _promptpayqr_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

        return invalid_parameters

    def _promptpayqr_form_validate(self, data):
        _logger.info('Validated transfer payment for tx %s: set as pending' % (self.reference))
        return self.write({'state': 'pending'})
