{
    'name': 'HR Applicant Custom',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Custom fields for HR Applicant',
    'description': 'Adds custom fields to the HR Applicant form.',
    'author': 'Your Name',
    'depends': ['hr_recruitment', 'website_hr_recruitment'],
    'data': [
        'views/assets.xml',
        'views/hr_applicant_templates.xml',
    ],
    'installable': True,
    'application': False,
}