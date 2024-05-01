# Generated by Django 5.0.2 on 2024-03-26 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_user_resume_pdf_alter_jobs_education_three_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='holland_code',
            field=models.ManyToManyField(to='core.holland_code'),
        ),
        migrations.AlterField(
            model_name='user',
            name='resume_pdf',
            field=models.FileField(blank=True, null=True, upload_to='api/pdf/{self.username}/pdf'),
        ),
    ]
