from odoo.addons.hr_applicant_custom.controllers.main import CustomWebsiteHrRecruitment
from odoo.http import Controller

# Check if our controller class is registered
print("Is CustomWebsiteHrRecruitment a Controller?", issubclass(CustomWebsiteHrRecruitment, Controller))

# Check model fields and create test record
applicant_fields = env['hr.applicant']._fields
print("\nCustom fields:")
for field in ['nin', 'gender', 'years_of_experience', 'highest_education_level', 
              'highest_degree_or_certificate', 'professional_body']:
    if field in applicant_fields:
        print(f"{field}: {applicant_fields[field].type}")

# Try to create a test record
test_record = env['hr.applicant'].sudo().create({
    'name': 'Test Applicant',
    'nin': 'TEST123',
    'gender': 'male',
    'years_of_experience': 5,
    'highest_education_level': 'Bachelor',
    'highest_degree_or_certificate': 'BSc',
    'professional_body': 'TEST'
})
print("\nTest record created:", test_record.id)
print("Fields values:")
for field in ['nin', 'gender', 'years_of_experience', 'highest_education_level']:
    print(f"{field}: {getattr(test_record, field)}")

env.cr.commit()
