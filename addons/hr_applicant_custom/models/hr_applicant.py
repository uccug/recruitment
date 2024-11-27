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
    @api.model
    def action_send_stage_email(self, stage_id):
        applicants = self.search([('stage_id', '=', stage_id)])
        
        if not applicants:
            raise UserError('No applicants found in this stage.')

        template = self.env.ref('hr_applicant_custom.email_template_stage_notification', raise_if_not_found=False)
        if not template:
            raise UserError('Email template not found!')

        for applicant in applicants:
            template.send_mail(applicant.id, force_send=True)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success!',
                'message': 'Emails sent to {} applicant(s)'.format(len(applicants)),
                'type': 'success',
                'sticky': False,
            }
        }