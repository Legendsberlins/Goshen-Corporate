from django.db import migrations


def seed_open_roles(apps, schema_editor):
    Job = apps.get_model('jobs', 'Job')

    jobs_data = [
        {
            'title': 'Administrative Assistant',
            'location': 'uyo-abuja',
            'job_type': 'full-time',
            'description': (
                'We are seeking a detail-oriented Administrative Assistant to support our operations '
                'in Uyo and Abuja. You will coordinate schedules, manage records, support meetings, '
                'and ensure smooth day-to-day execution across teams.'
            ),
            'requirements': (
                '- HND/BSc or equivalent qualification\n'
                '- 1-3 years of administrative or office support experience\n'
                '- Strong written and verbal communication skills\n'
                '- Proficiency with Microsoft Office or Google Workspace\n'
                '- Excellent organization, confidentiality, and multitasking ability'
            ),
        },
        {
            'title': 'Supply Chain Operations Manager',
            'location': 'uyo',
            'job_type': 'full-time',
            'description': (
                'Lead end-to-end supply chain execution for procurement, warehousing, and distribution. '
                'You will optimize inventory flow, improve service levels, and collaborate with logistics '
                'partners to deliver efficient operations.'
            ),
            'requirements': (
                '- BSc in Supply Chain, Logistics, Engineering, or related field\n'
                '- 3+ years of supply chain or operations management experience\n'
                '- Experience with inventory planning and vendor performance management\n'
                '- Strong analytical and reporting skills\n'
                '- Proven ability to improve process efficiency and reduce operational cost'
            ),
        },
        {
            'title': 'Digital Marketing Specialist',
            'location': 'remote-hybrid',
            'job_type': 'full-time',
            'description': (
                'Drive digital growth through campaign planning, content strategy, and performance '
                'marketing across social and search channels. You will manage execution, track KPI '
                'performance, and optimize campaigns to increase qualified leads.'
            ),
            'requirements': (
                '- BSc in Marketing, Communications, or related discipline\n'
                '- 2+ years of digital marketing experience\n'
                '- Hands-on experience with social media and paid campaigns\n'
                '- Ability to use analytics tools for reporting and optimization\n'
                '- Strong copywriting and audience targeting skills'
            ),
        },
    ]

    for job_data in jobs_data:
        Job.objects.update_or_create(
            title=job_data['title'],
            defaults=job_data,
        )


def unseed_open_roles(apps, schema_editor):
    Job = apps.get_model('jobs', 'Job')
    Job.objects.filter(
        title__in=[
            'Administrative Assistant',
            'Supply Chain Operations Manager',
            'Digital Marketing Specialist',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_open_roles, unseed_open_roles),
    ]
