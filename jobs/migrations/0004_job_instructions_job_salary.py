# Generated by Django 5.0.2 on 2024-04-10 10:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0003_rename_jobbookmarks_jobbookmark_alter_job_company"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="instructions",
            field=models.CharField(default=django.utils.timezone.now, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="job",
            name="salary",
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
    ]