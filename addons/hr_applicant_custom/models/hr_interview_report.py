from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        _logger.info('=== Attachment Search Debug ===')
        _logger.info('Original domain: %s', domain)
        _logger.info('Context: %s', self.env.context)

        context = self.env.context
        domain = domain or []

        # Getting the active_id from context
        active_id = context.get('active_id')
        
        # Checking if we came from an interview report
        if active_id:
            # Trying to find the interview report record
            interview_report = self.env['hr.interview.report'].browse(active_id).exists()
            if interview_report:
                _logger.info('Found interview report: %s', interview_report)
                domain = [
                    ('res_model', '=', 'hr.interview.report'),
                    ('res_id', '=', active_id)
                ]

        _logger.info('Modified domain: %s', domain)
        return super(IrAttachment, self).search_read(domain=domain, fields=fields, 
                                                   offset=offset, limit=limit, order=order)

class HrInterviewReport(models.Model):
    _name = 'hr.interview.report'
    _description = 'Interview Reports'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char('Title', required=True, tracking=True)
    job_id = fields.Many2one('hr.job', string='Job Position', required=True, tracking=True)
    applicant_id = fields.Many2one('hr.applicant', string='Applicant', required=True, tracking=True,
                                  domain="[('job_id', '=', job_id)]")
    date = fields.Date('Interview Date', required=True, tracking=True)
    interviewer_ids = fields.Many2many('res.users', string='Interviewers', tracking=True)
    report = fields.Html('Report', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved')
    ], string='Status', default='draft', tracking=True)
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_interview_report_ir_attachments_rel',
        'report_id',
        'attachment_id',
        string='Attachments',
        copy=False
    )

    @api.multi
    def _get_attachment_number(self):
        for record in self:
            record.attachment_number = len(record.attachment_ids)

    @api.model
    def create(self, vals):
        record = super(HrInterviewReport, self).create(vals)
        if record.attachment_ids:
            record.attachment_ids.write({
                'res_model': 'hr.interview.report',
                'res_id': record.id
            })
        return record

    @api.multi
    def write(self, vals):
        result = super(HrInterviewReport, self).write(vals)
        if 'attachment_ids' in vals:
            self.attachment_ids.write({
                'res_model': 'hr.interview.report',
                'res_id': self.id
            })
        return result

    @api.multi
    def action_get_attachment_tree_view(self):
        self.ensure_one()
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.id,
            'active_id': self.id,  # Making sure active_id is set
            'active_model': self._name,  # Trying to preserve active_model
        }
        action['domain'] = [
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)
        ]
        # Add params to URL
        action['params'] = {
            'model': self._name,
            'res_id': self.id,
            'active_id': self.id,
            'active_model': self._name
        }
        return action
  