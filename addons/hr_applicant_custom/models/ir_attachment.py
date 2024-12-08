from odoo import models, api
    
class IrAttachment(models.Model):
    """
    Inherit ir.attachment to customize attachment search behavior for:
    - Interview reports
    - Job applications
    
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
        1. Uses the surviving 'active_id' to find the related record (interview report or job application)
        2. Reconstructs the correct domain filter if a relevant record is found
        """
        context = self.env.context
        domain = domain or []

        active_id = context.get('active_id')
        if active_id:
            # Try to find either an interview report or job application
            interview_report = self.env['hr.interview.report'].browse(active_id).exists()
            job_application = self.env['hr.applicant'].browse(active_id).exists()

            if interview_report:
                domain = [
                    ('res_model', '=', 'hr.interview.report'),
                    ('res_id', '=', active_id)
                ]
            elif job_application:
                domain = [
                    ('res_model', '=', 'hr.applicant'),
                    ('res_id', '=', active_id)
                ]

        return super(IrAttachment, self).search_read(domain=domain, fields=fields, 
                                                   offset=offset, limit=limit, order=order) 