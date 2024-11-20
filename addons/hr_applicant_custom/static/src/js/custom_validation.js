odoo.define('hr_applicant_custom.custom_validation', function (require) {
    'use strict';

    var sAnimation = require('website.content.snippets.animation');

    var FormValidation = sAnimation.Class.extend({
        selector: '.js_hr_recruitment_form',
        
        events: {
            'click .o_website_form_send': '_onFormSubmit',
            'input input': '_onFieldInput',
            'blur input, select': '_onFieldBlur',
            'blur input[type="file"]': '_onFileChange',
            'change select[name="highest_education_level"]': '_onEducationLevelChange',
            'change input[type="file"]': '_onFileChange',
        },

        maxSizes: {
            'resume': 2 * 1024 * 1024,        // 2MB
            'academic_documents': 5 * 1024 * 1024  // 5MB
        },

        start: function () {
            this._super.apply(this, arguments);
            return this;
        },
        _onFileChange: function(ev) {
            var $input = $(ev.target);
            var fileName = $input.attr('name');
            var file = ev.target.files[0];
            var $feedback = $input.siblings('.invalid-feedback');
            
            if (file) {
                var maxSize = this.maxSizes[fileName];
                if (file.size > maxSize) {
                    var sizeMB = maxSize / (1024 * 1024);
                    $input.addClass('is-invalid');
                    $feedback.text(`File size exceeds ${sizeMB}MB limit. Reduce file size and upload again.`);
                    return false;
                }
            }   
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
                    
                    // To be improved. not needed
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
        _showAlert: function($form, message, type = 'danger') {
            // Remove any existing alerts
            $form.find('.validation-alert').remove();
            
            // Create Bootstrap alert
            var alertHtml = '<div class="alert alert-' + type + ' validation-alert alert-dismissible fade show" role="alert">' +
                '<strong>' + (type === 'danger' ? 'Error!' : 'Success!') + '</strong> ' + message +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span></button>' +
                '</div>';
                
            // Insert alert at top of form
            $form.prepend(alertHtml);
            
            // Scroll to alert
            $('html, body').animate({
                scrollTop: $form.find('.validation-alert').offset().top - 100
            }, 500);
        },

        _onFormSubmit: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            
            var self = this;
            var $form = $(ev.target).closest('form');
            var $submitButton = $(ev.target);
            var originalText = $submitButton.text();
            
            var isValid = true;
            var errorMessages = {
                required: [],
                files: []
            };

            
            $form.find('input[required], select[required], textarea[required]').each(function () {
                if (!self._validateField($(this))) {
                    isValid = false;
                    var fieldName = $field.closest('.form-group').find('label').text() || $field.attr('name');
                    errorMessages.required.push(fieldName.trim());
                }
            });

            $form.find('input[type="file"]').each(function() {
                var $input = $(this);
                var file = this.files[0];
                if (file) {
                    var maxSize = self.maxSizes[$input.attr('name')];
                    if (file.size > maxSize) {
                        isValid = false;
                        var sizeMB = maxSize / (1024 * 1024);
                        var fieldName = $input.closest('.form-group').find('label').text() || $input.attr('name');
                        errorMessages.files.push(`${fieldName} exceeds ${sizeMB}MB limit`);
                        return false;
                    }
                }
            });

            if (!isValid) {
                var alertContent = '';

                if (errorMessages.required.length) {
                    alertContent += '<strong>Required fields missing:</strong><br/>' +
                                  '<ul><li>' + errorMessages.required.join('</li><li>') + '</li></ul>';
                }

                if (errorMessages.files.length) {
                    alertContent += '<strong>File size errors:</strong><br/>' +
                                  '<ul><li>' + errorMessages.files.join('</li><li>') + '</li></ul>';
                }

                var alertHtml = '<div class="alert alert-danger validation-alert" role="alert">' +
                    alertContent +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                    '<span aria-hidden="true">&times;</span></button>' +
                    '</div>';
                
                // Insert alert at top of form
                $form.prepend(alertHtml);
                
                // Scroll to alert
                $('html, body').animate({
                    scrollTop: $form.find('.validation-alert').offset().top - 100
                }, 500);

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
                            self._showAlert($form, result.error_message || 'An unexpected error occurred. Please try again.', 'danger');
                        } else {
                            window.location.href = result.redirect_url || '/job-thank-you';
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                        self._showAlert($form, 'An error occurred while processing your request. Please try again.', 'danger');
                    }
                    $submitButton.prop('disabled', false).text(originalText);
                },
                error: function (xhr, status, error) {
                    console.error('Ajax error:', status, error);
                    console.error('Response:', xhr.responseText);
                    var errorMessage = 'An error occurred while submitting your application. ';
                    switch(xhr.status) {
                        case 404:
                            errorMessage += 'The submission endpoint was not found.';
                            break;
                        case 413:
                            errorMessage += 'The files you are trying to upload may be too large.';
                            break;
                        case 500:
                            errorMessage += 'There was a server error. Please try again later.';
                            break;
                        default:
                            errorMessage += 'Please try again later.';
                    }
                    
                    self._showAlert($form, errorMessage, 'danger');
                    $submitButton.prop('disabled', false).text(originalText);
                }
            });
        }
    });

    sAnimation.registry.formValidation = FormValidation;
    return FormValidation;
});