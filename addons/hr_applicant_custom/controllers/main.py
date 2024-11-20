import base64
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

    @http.route('/website/form/hr.applicant', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def website_form(self, **kwargs):
        print("="*80)
        print("Form submission received")
        print("POST data:", kwargs)
        
        try:
            vals = {
                'name': kwargs.get('partner_name', 'Unknown'),
                'partner_name': kwargs.get('partner_name'),
                'email_from': kwargs.get('email_from'),
                'partner_phone': kwargs.get('partner_phone'),
                'description': kwargs.get('description', ''),
                'job_id': int(kwargs.get('job_id')) if kwargs.get('job_id') else False, 
                'nin': kwargs.get('nin'),
                'gender': kwargs.get('gender'),
                'years_of_experience': int(kwargs.get('years_of_experience', '0')),
                'highest_education_level': kwargs.get('highest_education_level'),
                'highest_degree_or_certificate': kwargs.get('highest_degree_or_certificate'),
                'professional_body': kwargs.get('professional_body'),
            }

            # Create applicant first
            applicant = request.env['hr.applicant'].sudo().create(vals)
            print("Created applicant with ID:", applicant.id)

            # Handle Resume
            if kwargs.get('resume'):
                resume_file = kwargs.get('resume')
                attachment_value = {
                    'name': resume_file.filename,
                    'datas': base64.b64encode(resume_file.read()),
                    'res_model': 'hr.applicant',
                    'res_id': applicant.id,
                    'type': 'binary',
                    'description': 'Resume/CV'
                }
                request.env['ir.attachment'].sudo().create(attachment_value)
                print("Resume uploaded:", resume_file.filename)

            # Handle Academic Documents
            if kwargs.get('academic_documents'):
                academic_file = kwargs.get('academic_documents')
                vals['academic_documents'] = base64.b64encode(academic_file.read())
                applicant.write({'academic_documents': vals['academic_documents']})
                print("Academic documents uploaded:", academic_file.filename)
            
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