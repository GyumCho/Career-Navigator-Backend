# Generated by Django 5.0.2 on 2024-03-22 13:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_job_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="job",
            old_name="name",
            new_name="title",
        ),
    ]