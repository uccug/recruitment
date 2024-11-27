odoo.define('hr_applicant_custom.kanban_column', function (require) {
    "use strict";

    console.log("...................hr_applicant_custom.kanban_column should be loaded...........")

    var core = require('web.core');
    var KanbanColumn = require('web.KanbanColumn');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var QWeb = core.qweb;

    KanbanColumn.include({
        init: function () {
            this._super.apply(this, arguments);
            // Add debug log
            console.log('KanbanColumn init', this.modelName);
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
                // Add debug log
                console.log('KanbanColumn start', self.modelName);
                
                if (self.modelName === 'hr.applicant') {
                    var $dropdown = self.$('.o_kanban_config .dropdown-menu');
                    if ($dropdown.length) {
                        $dropdown.append($('<a/>', {
                            role: 'menuitem',
                            class: 'dropdown-item o_column_send_email',
                            href: '#',
                            text: _t('Send Stage Email')
                        }));
                    }
                }
            });
        },

        _onSendStageEmail: function (event) {
            event.preventDefault();
            var self = this;
            
            Dialog.confirm(this, _t("Are you sure you want to send emails to all applicants in this stage?"), {
                confirm_callback: function () {
                    self._rpc({
                        model: 'hr.applicant',
                        method: 'action_send_stage_email',
                        args: [[self.id]],
                    }).then(function () {
                        self.do_notify(_t('Success'), _t('Emails sent successfully'));
                    }).guardedCatch(function (error) {
                        self.do_warn(_t('Error'), _t('Failed to send emails'));
                    });
                },
            });
        },
    });
}); 