# HR Applicant Custom Module

## Overview
This module extends Odoo's HR Recruitment functionality with custom features for managing job applications. It provides enhanced form validation, custom fields, and manual email management for the recruitment process.

# 🚨 Warning

> **⚠️ Important:**  
> It has been tested with odoo 12 community edition which is running in a docker container. It has not yet been tested with the enterprise version.



## Addressed requirements
- [X] Capture applicant's Resume and academic documents. Should only accept PDF files.
- [X] Capture user details
    - Full Name
    - Email
    - Phone contact
    - National Identification Number (NIN)
    - Gender
    - Years of experience
    - Highest level of education
    - Highest degree or certificate awarded
    - Membership in professional organization(s)
- [X] Show validation errors to the applicant
- [X] Send email notifications to candidates after submitting the application
- [X] Disable automatic emails on application stage for:
    - Initial application submission
    - Stage changes(when dragging applications throught different stages)
- [X] Allow a user to send emails to refused/rejected applicants
- [X] Close the application after the closing date
- [X] Show all applications, detailing their academic and professional qualifications as well as years of experience and relevant memberships
- [X] Functionality to generate a shortlist of candidates along with their qualifications - already existed. Can be achieved with the use of filters
- [X] Allow a user to add a reason when rejecting an application
- [X] Add feature to upload shortlisting and interview and management papers
- [X] Remove unnecessary filters on job applications.
- [X] Disable editing of job applications
- [ ] Restrict job application access to interviewers and for a specific period of time. HR should have access to applications all the time. 
- [ ] When the deadline has passed automatically archive the job. To be addressed after consulting the enterprise version
- [ ] Update job positions search to exclude archived jobs 


## Technical Details

### Dependencies
- `hr_recruitment`
- `website`
- `web`

### Installation
1. Copy module to your Odoo addons directory
2. Update apps list in Odoo
3. Install the module

### Configuration
1. Set up email templates for different recruitment stages
2. Configure stage interviewers
3. Customize form validation messages (optional)
