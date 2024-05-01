# Generated by Django 5.0.2 on 2024-04-19 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0017_alter_job_options_alter_jobapplication_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='feedback',
            field=models.TextField(blank=True, default='', verbose_name='feedback'),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='interviewed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='processed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='tested',
            field=models.BooleanField(default=False),
        ),
    ]
