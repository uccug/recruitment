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
    refuse_reason = fields.Text(string='Refusal Reason', tracking=True)
    stage_interviewer_id = fields.Many2one(
        'hr.stage.interviewer',
        string='Stage Interviewer',
        compute='_compute_stage_interviewer',
        store=True
    )

    @api.depends('job_id', 'stage_id')
    def _compute_stage_interviewer(self):
        for record in self:
            record.stage_interviewer_id = self.env['hr.stage.interviewer'].search([
                ('job_id', '=', record.job_id.id),
                ('stage_id', '=', record.stage_id.id)
            ], limit=1)

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

        # Queue the emails in the background
        self.with_context(active_ids=applicants.ids).send_stage_emails(stage.template_id.id)

        count = len(applicants)
        message = 'Sending email{} to {} applicant{}'.format(
            's' if count > 1 else '',
            count,
            's' if count > 1 else ''
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': message,
                'type': 'success'
            }
        }


    @api.model
    def send_stage_emails(self, template_id):
        """Send emails in background with auto-commit"""
        template = self.env['mail.template'].browse(template_id)
        active_ids = self._context.get('active_ids', [])
        
        for applicant_id in active_ids:
            template.with_context(auto_commit=True).send_mail(
                applicant_id, 
                force_send=True,
                raise_exception=False
            ) 
    # For even better performance when sending emails in Odoo Enterprise, we could use the queue job module:

    """ 
    Since we are sending emails in a stage manually, this method is used to disable automatic
    mail sending when updating the stage of an applicant. it adds a context to skip the stage email.
    """
    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            # Using context to disable automatic mail sending
            return super(HrApplicant, self.with_context(skip_stage_email=True)).write(vals)
        return super(HrApplicant, self).write(vals)

    """
    Overriding _track_template to skip automatic email sending when dragging applications
    """
    @api.multi
    def _track_template(self, changes):
        # Skipping automatic email if context flag(skip_stage_email) is set
        if self._context.get('skip_stage_email'):
            return {}
        return super(HrApplicant, self)._track_template(changes)

    @api.multi
    def archive_applicant(self):
        """Override archive method to show refuse reason wizard"""
        self.ensure_one()
        if self.active:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Refuse Application',
                'res_model': 'applicant.refuse.reason',
                'view_mode': 'form',
                'view_type': 'form',  # Required in Odoo 12
                'target': 'new',
                'context': {'active_id': self.id}
            }
        return super(HrApplicant, self).archive_applicant()