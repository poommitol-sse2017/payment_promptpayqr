# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PromtpayController(http.Controller):
    _accept_url = '/payment/promtpay/feedback'

    @http.route('/payment/promtpay/feedback', type='http', auth='none', csrf=False)
    def promtpay_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'promtpayqr')
        return werkzeug.utils.redirect(post.pop('return_url', '/'))
    

    