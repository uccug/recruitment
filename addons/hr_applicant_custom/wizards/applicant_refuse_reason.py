from odoo import models, fields, api

class ApplicantRefuseReason(models.TransientModel):
    _name = 'applicant.refuse.reason'
    _description = 'Application Refusal Reason'

    refuse_reason = fields.Text(string='Reason for Refusal', required=True)

    def action_refuse_with_reason(self):
        applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        applicant.write({
            'refuse_reason': self.refuse_reason,
            'active': False
        })
        return {'type': 'ir.actions.act_window_close'} 