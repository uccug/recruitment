odoo.define('hr_applicant_custom.custom_filters_menu', function (require) {
    "use strict";

    var FiltersMenu = require('web.FiltersMenu');

    FiltersMenu.include({
        /**
         * Override the init method to customize the fields shown in the "Add Custom Filter" dropdown
         * for the Job Applications view. This limits the available fields to a specific whitelist,
         * making the filter creation more user-friendly and relevant.
         * 
         * @override
         * @param {Widget} parent The parent widget
         * @param {Array} filters List of predefined filters
         * @param {Object} fields Dictionary of field definitions
         * @returns {void}
         */
        init: function (parent, filters, fields) {
            if (parent.fields_view && parent.fields_view.model === 'hr.applicant') {
                var allowedFields = [
                    'job_id',
                    'stage_id',
                    'gender',
                    'nin',
                    'degree',
                    'department_id',
                    'email_from', 
                    'partner_name', // Applicant's name
                    'highest_education_level',
                    'highest_degree_or_certificate',
                    'professional_body',
                    'years_of_experience'
                ];

                var filteredFields = _.pick(fields, function (field, name) {
                    return allowedFields.includes(name);
                });

                this._super(parent, filters, filteredFields);
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
}); 
