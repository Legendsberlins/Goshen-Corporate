# Goshen Giant Group - Careers Page Setup

## Project Structure

This is a Django-based careers page for Goshen Giant Group. The project includes:

- **models.py**: Defines Job, Company, and GeneralApplication models
- **views.py**: Handles the careers page, job details, and application forms
- **urls.py**: URL routing for the careers application
- **templates/**: HTML templates for the careers page layout
- **admin.py**: Django admin configuration for managing jobs and applications

## Features

✅ **Main Careers Page** - Hero section, company overview, benefits, and job listings
✅ **Job Listings** - Browse all open positions with location and type filters
✅ **Job Details** - View full job description, requirements, and apply button
✅ **Job Applications** - Apply for specific positions with resume upload
✅ **General Applications** - Submit a general application to join the talent pool
✅ **Admin Dashboard** - Manage jobs, companies, and applications through Django admin
✅ **Responsive Design** - Mobile-friendly with Bootstrap 5

## Setup Instructions

### 1. Install Dependencies

```bash
cd c:\Users\akpan\Space\djangolearn\goshen-corporate\venv\Scripts
pip install django
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a Superuser

```bash
python manage.py createsuperuser
```

### 4. Add Sample Data

You have two options:

#### Option A: Add data through Django Admin

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Visit http://localhost:8000/admin/
3. Login with your superuser credentials
4. Add Companies:
   - Goshen Giant Foods Limited - Food processing & manufacturing
   - Agro Global Logistics Limited - Transportation & logistics
   - Goshen Giant Integrated Farms - Aquaculture & agriculture
   - Naturius Labs Laboratory services Limited - Analytical laboratory services

5. Add Sample Jobs:
   - Administrative Assistant (Uyo/Abuja, Full-Time)
   - Supply Chain Operations Manager (Uyo, Full-Time)
   - Digital Marketing Specialist (Remote/Hybrid)

#### Option B: Use the provided seed script

Create a file named `seed_data.py` in the same directory as `manage.py`:

```python
from jobs.models import Company, Job
from django.utils import timezone

# Create Companies
companies_data = [
    {
        'name': 'Goshen Giant Foods Limited',
        'description': 'Food processing & manufacturing',
        'order': 1
    },
    {
        'name': 'Agro Global Logistics Limited',
        'description': 'Transportation & logistics',
        'order': 2
    },
    {
        'name': 'Goshen Giant Integrated Farms',
        'description': 'Aquaculture & agriculture',
        'order': 3
    },
    {
        'name': 'Naturius Labs Laboratory services Limited',
        'description': 'Analytical laboratory services',
        'order': 4
    }
]

for company_data in companies_data:
    Company.objects.get_or_create(
        name=company_data['name'],
        defaults={'description': company_data['description'], 'order': company_data['order']}
    )

# Create Sample Jobs
jobs_data = [
    {
        'title': 'Administrative Assistant',
        'location': 'uyo',
        'job_type': 'full-time',
        'description': 'We are seeking a detail-oriented Administrative Assistant to support our growing team. You will be responsible for managing schedules, organizing meetings, and ensuring smooth day-to-day operations.',
        'requirements': '• High school diploma or equivalent\n• 1-2 years of administrative experience\n• Proficiency in Microsoft Office Suite\n• Excellent communication and organizational skills\n• Ability to multitask and prioritize effectively'
    },
    {
        'title': 'Supply Chain Operations Manager',
        'location': 'uyo',
        'job_type': 'full-time',
        'description': 'Lead our supply chain operations and ensure efficient logistics across our distribution network. You will oversee inventory management, supplier relationships, and process optimization.',
        'requirements': '• Bachelor\'s degree in Supply Chain, Logistics, or Business\n• 3+ years of supply chain management experience\n• Knowledge of inventory management systems\n• Strong analytical and problem-solving skills\n• Experience with process optimization and cost reduction'
    },
    {
        'title': 'Digital Marketing Specialist',
        'location': 'remote',
        'job_type': 'full-time',
        'description': 'Join our marketing team to develop and execute digital marketing strategies. You will manage social media, email campaigns, and digital content to build brand awareness.',
        'requirements': '• Bachelor\'s degree in Marketing, Communications, or related field\n• 2+ years of digital marketing experience\n• Proficiency in social media platforms and tools\n• Experience with Google Analytics and email marketing platforms\n• Creative thinking and strong copywriting skills'
    }
]

for job_data in jobs_data:
    Job.objects.get_or_create(
        title=job_data['title'],
        defaults={
            'location': job_data['location'],
            'job_type': job_data['job_type'],
            'description': job_data['description'],
            'requirements': job_data['requirements']
        }
    )

print("Sample data created successfully!")
```

Then run:

```bash
python manage.py shell < seed_data.py
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/careers/

## URL Routes

- `/careers/` - Main careers page
- `/careers/jobs/<id>/` - Job details page
- `/careers/jobs/<id>/apply/` - Apply for a specific job
- `/careers/apply/general/` - Submit general application
- `/admin/` - Django admin panel

## File Uploads

The application supports resume uploads. Make sure you have:
1. Created a `media/` directory in your project root
2. Configured `MEDIA_URL` and `MEDIA_ROOT` in settings.py

Add this to your `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

And add this to your `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Customization

### Modify the Layout

The main styles are in `templates/base.html` within the `<style>` tag. You can customize:
- Colors (primary, secondary, accent)
- Font sizes and weights
- Spacing and padding
- Button styles

### Add More Companies

Edit the companies section in `templates/jobs/careers.html` or add through Django admin.

### Add More Jobs

Jobs can be added through:
1. Django admin at `/admin/` (recommended)
2. Directly through the management shell

## Next Steps

1. Configure email settings for application notifications (optional)
2. Add more companies and job positions
3. Customize the branding and colors to match your brand guidelines
4. Deploy to production (Heroku, AWS, DigitalOcean, etc.)
