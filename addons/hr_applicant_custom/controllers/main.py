import base64
from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class CustomWebsiteHrRecruitment(http.Controller):
    # File size limits in bytes
    MAX_SIZES = {
        'resume': 2 * 1024 * 1024,        # 2MB
        'academic_documents': 5 * 1024 * 1024  # 5MB
    }
    
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
            # Validate file sizes
            for field_name, file_data in kwargs.items():
                if hasattr(file_data, 'read') and field_name in self.MAX_SIZES:
                    if len(file_data.read()) > self.MAX_SIZES[field_name]:
                        size_mb = self.MAX_SIZES[field_name] / (1024 * 1024)
                        return json.dumps({
                            'error': True,
                            'error_message': 'File size exceeds {}MB limit for {}'.format(size_mb, field_name)
                        })
                    file_data.seek(0)  # Reset file pointer after reading

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

            if kwargs.get('academic_documents'):
                academic_file = kwargs.get('academic_documents')
                attachment_value = {
                    'name': academic_file.filename,
                    'datas': base64.b64encode(academic_file.read()),
                    'res_model': 'hr.applicant',
                    'res_id': applicant.id,
                    'type': 'binary',
                    'description': 'Academic Documents'
                }
                request.env['ir.attachment'].sudo().create(attachment_value)
                print("Academic documents uploaded:", academic_file.filename)

            try:
                template_id = request.env.ref('hr_applicant_custom.email_template_application_received')
                if template_id:
                    template_id.sudo().with_context(
                        lang=request.env.user.lang
                    ).send_mail(
                        applicant.id,
                        force_send=True
                    )
                    _logger.info('Application confirmation email sent to %s', applicant.email_from)
            except Exception as e:
                _logger.error('Failed to send application email: %s', str(e))
            
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