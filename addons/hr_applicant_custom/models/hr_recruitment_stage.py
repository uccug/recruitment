from odoo import models, fields, api

class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    stage_interviewer_ids = fields.One2many(
        'hr.stage.interviewer',
        'stage_id',
        string='Job-Specific Interviewers'
    )

    job_id = fields.Many2one('hr.job', string='Job Position')

    @api.onchange('stage_interviewer_ids')
    def _onchange_stage_interviewer_ids(self):
        for record in self:
            for interviewer in record.stage_interviewer_ids:
                if not interviewer.job_id:
                    interviewer.job_id = record.job_id
                if not interviewer.stage_id:
                    interviewer.stage_id = record.id 