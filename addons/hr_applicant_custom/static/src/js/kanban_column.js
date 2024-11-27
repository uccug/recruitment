odoo.define('hr_applicant_custom.kanban_column', function (require) {
    "use strict";

    var core = require('web.core');
    var KanbanColumn = require('web.KanbanColumn');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var QWeb = core.qweb;

    KanbanColumn.include({
        init: function () {
            this._super.apply(this, arguments);
        },

        events: _.extend({}, KanbanColumn.prototype.events, {
            'click .o_column_send_email': '_onSendStageEmail',
        }),

        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.modelName === 'hr.applicant') {
                    var $dropdown = self.$('.o_kanban_config .dropdown-menu');
                    if ($dropdown.length) {
                        $dropdown.append($('<a/>', {
                            role: 'menuitem',
                            class: 'dropdown-item o_column_send_email',
                            href: '#',
                            text: _t('Send Stage Emails')
                        }));
                    }
                }
            });
        },

        _onSendStageEmail: function (event) {
            event.preventDefault();
            var self = this;

            // Getting the current job_id from the parent view
            var parent = this.getParent();
            var job_id = parent && parent.state && parent.state.domain && 
                        _.find(parent.state.domain, function(item) {
                            return item[0] === 'job_id' && item[1] === '=';
                        });
            
            job_id = job_id && job_id[2];

            if (!job_id) {
                this.do_warn(_t('Error'), _t('Could not determine the current job position.'));
                return;
            }
            
            Dialog.confirm(this, _t("Are you sure you want to send emails to applicants in this stage?"), {
                confirm_callback: function () {
                    // Showing immediate feedback
                    self.do_notify(_t('Info'), _t('Sending emails in background...'));
                    
                    self._rpc({
                        model: 'hr.applicant',
                        method: 'action_send_stage_email',
                        args: [[self.id]],
                        kwargs: {
                            'job_id': job_id,
                        }
                    }, {
                        shadow: true  // Prevents the loading indicator
                    }).then(function (result) {
                        if (result && result.params) {
                            self.do_notify(_t('Success'), result.params.message);
                        }
                    }).fail(function (error) {
                        self.do_warn(_t('Error'), _t('Failed to send emails'));
                    });
                },
            });
        },
    });
}); 