from odoo import models, fields, api
from bs4 import BeautifulSoup

class HrInterviewReport(models.Model):
    _name = 'hr.interview.report'
    _description = 'Interview Reports'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char('Title', required=True, tracking=True)
    job_id = fields.Many2one('hr.job', string='Job Position', required=True, tracking=True)
    applicant_id = fields.Many2one('hr.applicant', string='Applicant', tracking=True,
                                  domain="[('job_id', '=', job_id)]")
    date = fields.Date('Interview Date', tracking=True)
    interviewer_ids = fields.Many2many('res.users', string='Interviewers', tracking=True)
    report = fields.Html('Report', required=True, tracking=True)
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_interview_report_ir_attachments_rel',
        'report_id',
        'attachment_id',
        string='Attachments',
        copy=False,
        tracking=True 
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
        """
        Override the write method to manually track changes to fields and attachments.

        Note:
        - Inheriting from mail.thread and setting tracking=True on fields should automatically
          track changes in the chatter. However, for some unknown reason, this was not working
          as expected in this module.
        - As a workaround, we manually track changes to ensure updates are logged in the chatter.
        - If the root cause is identified and resolved, we can revert to relying solely on
          mail.thread and tracking=True for automatic tracking.

        Args:
            vals (dict): The fields and values to update.

        Returns:
            bool: True if the write operation was successful.
        """
        tracked_changes = []
        attachment_changes = []
        
        for record in self:
            # Special handling for attachments
            if 'attachment_ids' in vals:
                old_attachments = record.attachment_ids
                command = vals['attachment_ids'][0] if vals['attachment_ids'] else False
                
                if command and command[0] == 6:  # Replace command
                    new_attachments = self.env['ir.attachment'].browse(command[2])
                    added = new_attachments - old_attachments
                    removed = old_attachments - new_attachments
                    
                    if added:
                        attachment_changes.append((record, u"Added document(s): {}".format(
                            ', '.join(added.mapped('name'))
                        )))
                    if removed:
                        attachment_changes.append((record, u"Removed document(s): {}".format(
                            ', '.join(removed.mapped('name'))
                        )))

            # Handle other tracked fields
            for field, new_value in vals.items():
                if field != 'attachment_ids':
                    field_obj = record._fields.get(field)
                    if field_obj and field_obj.tracking:
                        if field in record._fields:
                            if field_obj.type == 'html':
                                old_value = record[field]
                                # Compare stripped text content
                                old_text = BeautifulSoup(old_value or '', 'html.parser').get_text().strip()
                                new_text = BeautifulSoup(new_value or '', 'html.parser').get_text().strip()
                                if old_text != new_text:
                                    tracked_changes.append((record, u"{}: {} → {}".format(
                                        field_obj.string,
                                        old_text or 'None',
                                        new_text or 'None'
                                    )))
                            elif field_obj.type == 'many2one':
                                old_value = record[field].name_get()[0][1] if record[field] else False
                                new_record = record.env[field_obj.comodel_name].browse(new_value) if new_value else False
                                new_value_display = new_record.name_get()[0][1] if new_record else False
                                if old_value != new_value_display:
                                    tracked_changes.append((record, u"{}: {} → {}".format(
                                        field_obj.string, 
                                        old_value or 'None', 
                                        new_value_display or 'None'
                                    )))
                            elif field_obj.type == 'many2many':
                                old_values = [name for id, name in record[field].name_get()]
                                new_records = record.env[field_obj.comodel_name].browse(new_value[0][2]) if new_value else []
                                new_values = [name for id, name in new_records.name_get()]
                                if set(old_values) != set(new_values):
                                    tracked_changes.append((record, u"{}: {} → {}".format(
                                        field_obj.string,
                                        ', '.join(old_values) or 'None',
                                        ', '.join(new_values) or 'None'
                                    )))
                            else:
                                old_value = record[field]
                                print("*" * 80)
                                print("Old value:", old_value, "New value:", new_value)
                                if old_value != new_value:
                                    print("==== True Old value:", old_value, "New value:", new_value)
                                    tracked_changes.append((record, u"{}: {} → {}".format(
                                        field_obj.string,
                                        old_value or 'None',
                                        new_value or 'None'
                                    )))
                                print("*" * 80)

        # Perform the update
        result = super(HrInterviewReport, self).write(vals)
        
        # Handle attachment updates
        if 'attachment_ids' in vals:
            self.attachment_ids.write({
                'res_model': 'hr.interview.report',
                'res_id': self.id
            })

        # Post messages for tracked changes (non-attachments)
        for record, message in tracked_changes:
            record.message_post(
                body=u"<b>Updated Fields:</b><br/>" + message,
                message_type='notification'
            )

        # Post messages for attachment changes separately
        for record, message in attachment_changes:
            record.message_post(
                body=message,
                message_type='notification'
            )

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
  