import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HrStageInterviewer(models.Model):
    _name = 'hr.stage.interviewer'
    _description = 'Stage Interviewers for Job Positions'

    job_id = fields.Many2one('hr.job', string='Job Position', required=True)
    stage_id = fields.Many2one('hr.recruitment.stage', string='Stage', required=True)
    interviewer_ids = fields.Many2many(
        'res.users', 
        'stage_job_interviewer_rel',
        'stage_job_id',
        'user_id',
        string='Interviewers'
    )
    start_date = fields.Date(string='Access Start Date', required=True)
    end_date = fields.Date(string='Access End Date', required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_job_stage', 
         'UNIQUE(job_id, stage_id)', 
         'Interviewers are already defined for this job position and stage!')
    ]

    @api.model
    def get_user_accessible_application_ids(self, user_id=None):
        """
        Get all application IDs accessible to a specific user based on:
        - Their interviewer assignments
        - Current date within access period
        """
        if user_id is None:
            user_id = self.env.user.id
            
        today = fields.Date.today()
        stage_interviewers = self.search([
            ('interviewer_ids', 'in', user_id),
            ('start_date', '<=', today),
            ('end_date', '>=', today)
        ])
        
        applications = self.env['hr.applicant'].search([
            ('job_id', 'in', stage_interviewers.mapped('job_id').ids),
            ('stage_id', 'in', stage_interviewers.mapped('stage_id').ids)
        ])
        
        return applications.ids 

    @api.model
    def create(self, vals):
        _logger.error('CREATE called with vals: %s', vals)
        if not vals.get('job_id') and vals.get('stage_id'):
            stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            _logger.error('Stage found: %s', stage)
            _logger.error('Stage job_id: %s', stage.job_id.id if stage.job_id else None)
            if stage.job_id:
                vals['job_id'] = stage.job_id.id
            else:
                raise ValidationError('No job position found for the selected stage!')
        return super(HrStageInterviewer, self).create(vals)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        _logger.error('ONCHANGE called with stage_id: %s', self.stage_id)
        if self.stage_id and self.stage_id.job_id:
            _logger.error('Setting job_id to: %s', self.stage_id.job_id.id)
            self.job_id = self.stage_id.job_id

    def write(self, vals):
        if not vals.get('job_id') and vals.get('stage_id'):
            stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            vals['job_id'] = stage.job_id.id
        return super().write(vals) 

    @api.model
    def default_get(self, fields_list):
        res = super(HrStageInterviewer, self).default_get(fields_list)
        if self._context.get('active_id'):
            stage = self.env['hr.recruitment.stage'].browse(self._context.get('active_id'))
            if stage.exists():
                res['stage_id'] = stage.id
                res['job_id'] = stage.job_id.id
                print("====DEFAULT GET==== ", stage.job_id.id, stage.id)
        return res 