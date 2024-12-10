odoo.define('hr_applicant_custom.custom_filters_menu', function (require) {
    "use strict";

    var FiltersMenu = require('web.FiltersMenu');

    // Setting selectable=False on model fields is the best option but it was not taking effect which made it hard to control field visibility.
    // We resorted to a white list for the moment
    var allowedFields = {
        'hr.applicant': [
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
        ],
        'hr.interview.report': [
            'name',
            'date',
            'applicant_id',
            'interviewer_ids',
            'job_id'
        ]
    };

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
            if (parent.fields_view && allowedFields.hasOwnProperty(parent.fields_view.model)) {
                var filteredFields = _.pick(fields, function (field, name) {
                    return allowedFields[parent.fields_view.model].includes(name);
                });

                this._super(parent, filters, filteredFields);
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
}); 
