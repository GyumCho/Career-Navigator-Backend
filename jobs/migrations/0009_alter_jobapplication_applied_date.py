# Generated by Django 5.0.2 on 2024-04-16 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0008_rename_applied_time_jobapplication_applied_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="applied_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
