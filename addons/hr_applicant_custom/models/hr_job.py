from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class HrJob(models.Model):
    _inherit = 'hr.job'

    application_deadline = fields.Date(string='Application Deadline')
    is_deadline_passed = fields.Boolean(
        string='Deadline Passed',
        compute='_compute_is_deadline_passed',
        store=True
    )

    @api.depends('application_deadline')
    def _compute_is_deadline_passed(self):
        today = fields.Date.today()
        for job in self:
            job.is_deadline_passed = bool(job.application_deadline and job.application_deadline < today)

    @api.constrains('application_deadline')
    def _check_deadline_date(self):
        for job in self:
            if job.application_deadline and job.application_deadline < fields.Date.today():
                raise ValidationError('Application deadline cannot be in the past.')