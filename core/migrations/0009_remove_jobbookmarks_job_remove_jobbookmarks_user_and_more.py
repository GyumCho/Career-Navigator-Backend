# Generated by Django 5.0.2 on 2024-03-25 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_name_job_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobbookmarks',
            name='job',
        ),
        migrations.RemoveField(
            model_name='jobbookmarks',
            name='user',
        ),
        migrations.DeleteModel(
            name='Job',
        ),
        migrations.DeleteModel(
            name='JobBookMarks',
        ),
    ]
