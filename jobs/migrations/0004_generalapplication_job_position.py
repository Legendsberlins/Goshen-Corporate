from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_alter_job_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='jobs.job'),
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='position_applied',
            field=models.CharField(blank=True, help_text='Job title applied for (including unlisted roles)', max_length=255),
        ),
    ]
