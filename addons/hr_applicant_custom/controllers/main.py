from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class CustomWebsiteHrRecruitment(http.Controller):
    
    @http.route('/applicant/test', type='http', auth='public', website=True)
    def test_route(self):
        print("Test route accessed!")
        return "Controller is working!"

    @http.route('/website/form/hr.applicant', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def website_form(self, **kwargs):
        print("="*80)
        print("Form submission received")
        print("POST data:", kwargs)
        
        try:
            vals = {
                'name': kwargs.get('partner_name', 'Unknown'),
                'partner_name': kwargs.get('partner_name'),
                'email_from': kwargs.get('email_from'),
                'description': kwargs.get('description', ''),
                'nin': kwargs.get('nin'),
                'gender': kwargs.get('gender'),
                'years_of_experience': int(kwargs.get('years_of_experience', '0')),
                'highest_education_level': kwargs.get('highest_education_level'),
                'highest_degree_or_certificate': kwargs.get('highest_degree_or_certificate'),
                'professional_body': kwargs.get('professional_body'),
            }
            
            print("Creating applicant with vals:", vals)
            applicant = request.env['hr.applicant'].sudo().create(vals)
            print("Created applicant with ID:", applicant.id)
            
            return json.dumps({
                'success': True,
                'message': 'Application submitted successfully',
                'redirect_url': '/job-thank-you'
            })
            
        except Exception as e:
            print("Error:", str(e))
            return json.dumps({
                'error': True,
                'error_message': str(e)
            })