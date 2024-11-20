odoo.define('hr_applicant_custom.custom_validation', function (require) {
    'use strict';

    var sAnimation = require('website.content.snippets.animation');

    var FormValidation = sAnimation.Class.extend({
        selector: '.js_hr_recruitment_form',
        
        events: {
            'click .o_website_form_send': '_onFormSubmit',
            'input input': '_onFieldInput',
            'blur input, select': '_onFieldBlur',
            'change select[name="highest_education_level"]': '_onEducationLevelChange' 
        },

        start: function () {
            this._super.apply(this, arguments);
            return this;
        },

        _onEducationLevelChange: function (ev) {
            var $select = this.$('select[name="highest_education_level"]');
            var $otherInput = this.$("#other_highest_education_level").closest('.form-group');
            
            if ($select.val() === 'other') {
                $otherInput.removeClass('d-none');
                $otherInput.find('input').prop('required', true);
            } else {
                $otherInput.addClass('d-none');
                $otherInput.find('input').prop('required', false).val('');
            }
        },

        _onFieldInput: function (ev) {
            this._validateField($(ev.target));
        },

        _onFieldBlur: function (ev) {
            this._validateField($(ev.target));
        },

        _validateField: function($field) {
            var isValid = true;
            var value = $field.val().trim();
            var $feedback = $field.siblings('.invalid-feedback');
            
            // Clear previous validation state
            $field.removeClass('is-invalid is-valid');

            // Required field validation
            if ($field.prop('required') && !value) {
                isValid = false;
                // Use feedback div text, data attribute, or fallback message
                var requiredMessage = $feedback.text() || 
                                    $field.data('required-message') || 
                                    'This field is required';
                $feedback.text(requiredMessage);
            } 

            // Field-specific validation (only if field has a value)
            else if (value) {
                switch($field.attr('name')) {
                    case 'email_from':
                        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (!emailRegex.test(value)) {
                            isValid = false;
                            var invalidEmailMsg = $field.data('invalid-message') || 
                                                'Please enter a valid email address';
                            $feedback.text(invalidEmailMsg);
                        }
                        break;

                    case 'nin':
                        var ninRegex = /^[A-Z]{2}[A-Za-z0-9]{12}$/;
                        if (value.length !== 14 || !ninRegex.test(value)) {
                            isValid = false;
                            var invalidNinMsg = $field.data('invalid-message') || "Enter a valid NIN Number"
                            $feedback.text(invalidNinMsg);
                        }
                        break;
                    
                    // To be improved.
                    case 'gender':
                        if (value === '') {
                            isValid = false;
                            $feedback.text('Gender is required');
                        }
                        break;
    
                    case 'highest_education_level':
                        if (value === '') {
                            isValid = false;
                            $feedback.text('Highest Level of Education is required');
                        }
                        break;
                }
            }

            if (!isValid) {
                $field.addClass('is-invalid');
            } else {
                $field.addClass('is-valid');
                $feedback.text('');
            }

            return isValid;
        },

        _onFormSubmit: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            
            var self = this;
            var $form = $(ev.target).closest('form');
            var $submitButton = $(ev.target);
            var originalText = $submitButton.text();
            
            var isValid = true;
            $form.find('input[required], select[required], textarea[required]').each(function () {
                if (!self._validateField($(this))) {
                    isValid = false;
                }
            });

            if (!isValid) {
                return false;
            }

            $submitButton.prop('disabled', true).text('Submitting...');


            $.ajax({
                url: $form.attr('action'),
                type: 'POST',
                data: new FormData($form[0]),
                processData: false,
                contentType: false,
                success: function (response) {
                    try {
                        var result = JSON.parse(response);
                        if (result.error) {
                            console.error('Error response:', result.error);
                            alert(result.error_message || 'An error occurred');
                        } else {
                            window.location.href = result.redirect_url || '/job-thank-you';
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                        alert('An error occurred');
                    }
                    $submitButton.prop('disabled', false).text(originalText);
                },
                error: function (xhr, status, error) {

                    alert('Error submitting form');
                    $submitButton.prop('disabled', false).text(originalText);
                }
            });
        }
    });

    sAnimation.registry.formValidation = FormValidation;
    return FormValidation;
});