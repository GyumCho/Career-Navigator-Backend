# Generated by Django 5.0.2 on 2024-03-20 10:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_rename_jobid_jobbookmarks_job"),
    ]

    operations = [
        migrations.RenameField(
            model_name="jobbookmarks",
            old_name="owner",
            new_name="user",
        ),
    ]
