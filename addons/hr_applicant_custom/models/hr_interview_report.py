from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    """
    Inherit ir.attachment to customize attachment search behavior for interview reports.
    This is necessary because the attachment view loses its context and domain after page refresh,
    causing it to display all system attachments instead of only the relevant document attachments.
    """
    _inherit = 'ir.attachment'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Override search_read to maintain attachment filtering after page refresh.
        
        The original implementation loses the domain filter after refresh because:
        1. The context loses the 'default_res_model' and other model-specific parameters
        2. Only 'active_id' survives in the context after refresh
        
        This override:
        1. Uses the surviving 'active_id' to find the related interview report
        2. Reconstructs the correct domain filter if an interview report is found
        
        Args:
            domain: Search domain (empty after page refresh)
            fields: Fields to read
            offset: Query offset
            limit: Query limit
            order: Sort order
        
        Returns:
            Filtered attachment records
        """

        context = self.env.context
        domain = domain or []

        # Getting the active_id from context (this survives page refresh)
        active_id = context.get('active_id')
        
        # Checking if we came from an interview report by trying to find the record
        if active_id:
            interview_report = self.env['hr.interview.report'].browse(active_id).exists()
            if interview_report:
                # Reconstructing the domain to filter attachments for this report
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
        """
        Open the attachment view for the current interview report.
        
        This method:
        1. Sets up the initial context and domain for attachment filtering
        2. Includes 'active_id' in context which survives page refresh
        3. Adds URL parameters to help maintain context (though not all survive refresh)
        
        The attachment filtering is maintained after refresh by the ir.attachment
        search_read override, which uses the surviving 'active_id' parameter.
        
        Returns:
            dict: Action dictionary for the attachment view
        """
        self.ensure_one()
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.id,
            'active_id': self.id,  # This survives page refresh
            'active_model': self._name,
        }
        action['domain'] = [
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)
        ]
        # Adding URL parameters to help maintain context (some may be lost after refresh)
        action['params'] = {
            'model': self._name,
            'res_id': self.id,
            'active_id': self.id,
            'active_model': self._name
        }
        return action
  