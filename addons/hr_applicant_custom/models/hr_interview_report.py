from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

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
        # Update existing attachments first in case they were created without a res_id
        self.attachment_ids.write({
            'res_model': 'hr.interview.report',
            'res_id': self.id
        })
        
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.id
        }
        action['domain'] = [
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)
        ]
        return action
  