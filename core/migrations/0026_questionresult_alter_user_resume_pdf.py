# Generated by Django 5.0.2 on 2024-04-11 15:51

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_user_interest_alter_user_others_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('MbtiType', models.CharField(max_length=250)),
                ('codeOne', models.CharField(max_length=250)),
                ('codeTwo', models.CharField(max_length=250)),
                ('category_one', models.CharField(max_length=250)),
                ('category_two', models.CharField(max_length=250)),
                ('category_three', models.CharField(max_length=250)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='resume_pdf',
            field=models.FileField(blank=True, null=True, upload_to=core.models.upload_to_path),
        ),
    ]
