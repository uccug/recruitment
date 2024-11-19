import json
import base64
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class CustomWebsiteHrRecruitment(http.Controller):
    
    @http.route('/website_form/hr.applicant', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def website_form(self, **kwargs):
        _logger.info("="*80)
        _logger.info("Custom form handler called")
        _logger.info("POST data: %s", kwargs)

        try:
            vals = {
                'name': kwargs.get('partner_name', 'Unknown'),
                'partner_name': kwargs.get('partner_name'),
                'email_from': kwargs.get('email_from'),
                'description': kwargs.get('description'),
                # Custom fields
                'nin': kwargs.get('nin'),
                'gender': kwargs.get('gender'),
                'years_of_experience': int(kwargs.get('years_of_experience', '0')),
                'highest_education_level': kwargs.get('highest_education_level'),
                'highest_degree_or_certificate': kwargs.get('highest_degree_or_certificate'),
                'professional_body': kwargs.get('professional_body'),
            }

            _logger.info("Creating applicant with vals: %s", vals)
            applicant = request.env['hr.applicant'].sudo().create(vals)
            _logger.info("Created applicant ID: %s", applicant.id)

            return json.dumps({
                'success': True,
                'message': 'Application submitted successfully',
                'redirect_url': '/job-thank-you'
            })

        except Exception as e:
            _logger.exception("Error in form submission")
            return json.dumps({
                'error': True,
                'error_message': str(e)
            }) 