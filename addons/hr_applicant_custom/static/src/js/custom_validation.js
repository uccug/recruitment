console.log('1. File is being loaded');

// First module definition - Widget definition
odoo.define('hr_applicant_custom.custom_validation', function (require) {
    'use strict';

    console.log('2. Inside odoo.define');
    var sAnimation = require('website.content.snippets.animation');
    console.log('3. sAnimation loaded');

    var FormValidation = sAnimation.Class.extend({
        selector: '.js_hr_recruitment_form',
        
        events: {
            'click .o_website_form_send': '_onFormSubmit',
            'input input': '_onFieldInput',
            'blur input, select': '_onFieldBlur',
            'change select[name="highest_education_level"]': '_onEducationLevelChange' 
        },

        start: function () {
            console.log('4. Widget started');
            this._super.apply(this, arguments);
            console.log('Form found:', this.$el.length);
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
            console.log('Field input event triggered');
            this._validateField($(ev.target));
        },

        _onFieldBlur: function (ev) {
            console.log('Field blur event triggered');
            this._validateField($(ev.target));
        },

        _validateField: function($field) {
            console.log('Validating field:', $field.attr('name'));
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

            // Update field status
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
            
            // Validate if needed
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

            // Add form data manually if needed
            /*
            var formData = new FormData();
            $form.find('input, select, textarea').each(function() {
                var $input = $(this);
                var name = $input.attr('name');
                var value = $input.val();
                if (name) {
                    if ($input.attr('type') === 'file') {
                        var files = $input[0].files;
                        if (files.length > 0) {
                            formData.append(name, files[0]);
                        }
                    } else {
                        formData.append(name, value);
                    }
                }
            });
            */

            console.log('$form.att........>>>>> ', $form.attr('action'))


            // Submit form using AJAX
            $.ajax({
                url: $form.attr('action'),
                type: 'POST',
                data: new FormData($form[0]),  // Use the form element directly
                processData: false,
                contentType: false,
                success: function (response) {
                    try {
                        var result = JSON.parse(response);
                        if (result.error) {
                            alert(result.error_message || 'An error occurred');
                        } else {
                            // window.location.href = result.redirect_url || '/job-thank-you';
                            console.log('Redirecting to..........:', result.redirect_url || '/job-thank-you');
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                        alert('An error occurred');
                    }
                    $submitButton.prop('disabled', false).text(originalText);
                },
                error: function (xhr, status, error) {
                    console.error('Ajax error:', status, error);
                    console.error('Response:', xhr.responseText);
                    alert('Error submitting form');
                    $submitButton.prop('disabled', false).text(originalText);
                }
            });
        }
    });

    sAnimation.registry.formValidation = FormValidation;
    console.log('5. Widget registered');
    return FormValidation;
});