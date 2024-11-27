from odoo import models, fields, api
from odoo.exceptions import UserError

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    @api.model
    def website_form_input_filter(self, request, values):
        values = super(HrApplicant, self).website_form_input_filter(request, values)
        
        # Explicitly map fields
        for field in ['nin', 'gender', 'years_of_experience', 
                     'highest_education_level', 'highest_degree_or_certificate', 
                     'professional_body', 'academic_documents']:
            if field in values:
                values[field] = values[field]
        
        return values

    nin = fields.Char(string='NIN Number', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', tracking=True)
    years_of_experience = fields.Integer(string='Years of Experience', tracking=True)
    highest_education_level = fields.Char(string='Highest Education Level', tracking=True)
    highest_degree_or_certificate = fields.Char(string='Highest Degree or Certificate', tracking=True)
    professional_body = fields.Char(string='Professional Body', tracking=True)
    academic_documents = fields.Binary(string='Academic Documents', attachment=True, tracking=True)
    # use ir.attachment. and many to one for attachments

    """ 
    This method is used to send emails to applicants in a specific stage for a given job position.
    """
    @api.model
    def action_send_stage_email(self, stage_id, job_id=False):
        if not job_id:
            raise UserError('Job position not found. Please try again.')
        
        domain = [('stage_id', '=', stage_id), ('job_id', '=', job_id)]
            
        applicants = self.search(domain)
        
        if not applicants:
            raise UserError('No applicants found in this stage for the current job position.')

        stage = self.env['hr.recruitment.stage'].browse(stage_id)
        if not stage.template_id:
            raise UserError('No email template defined for this stage.')

        # Using the stage's template to send emails
        for applicant in applicants:
            stage.template_id.send_mail(applicant.id, force_send=True)

        count = len(applicants)
        message = 'Email{} sent to {} applicant{}'.format(
            's' if count > 1 else '',
            count,
            's' if count > 1 else ''
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success!',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        } 