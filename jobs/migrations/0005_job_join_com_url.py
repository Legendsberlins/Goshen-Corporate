# Generated migration for join.com URL field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_generalapplication_job_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='join_com_url',
            field=models.URLField(blank=True, null=True, help_text='Link to job posting on join.com'),
        ),
    ]
