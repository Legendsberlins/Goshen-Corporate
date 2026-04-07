from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_seed_open_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='location',
            field=models.CharField(
                choices=[
                    ('uyo', 'Uyo'),
                    ('abuja', 'Abuja'),
                    ('uyo-abuja', 'Uyo / Abuja'),
                    ('remote', 'Remote'),
                    ('hybrid', 'Hybrid'),
                    ('remote-hybrid', 'Remote / Hybrid'),
                ],
                max_length=50,
            ),
        ),
    ]
