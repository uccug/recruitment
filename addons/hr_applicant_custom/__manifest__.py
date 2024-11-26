{
    'name': 'HR Applicant Custom',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Custom fields for HR Applicant',
    'description': 'Adds custom fields to the HR Applicant form.',
    'author': 'Your Name',
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'website',
        'website_form',
        'website_hr_recruitment',
        'web'
        ],
    'data': [
        'views/hr_job_views.xml',
        'views/website_hr_recruitment_templates.xml',
        'views/hr_applicant_views.xml',
        'data/mail_template.xml',
        'views/assets.xml',
        'views/hr_applicant_templates.xml',
    ],
    'sequence': 100,
    'installable': True,
    'application': False,
    'auto_install': False
}