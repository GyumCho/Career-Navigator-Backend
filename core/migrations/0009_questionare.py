# Generated by Django 5.0.2 on 2024-03-27 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_jobs_holland_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_fix', models.CharField(max_length=250)),
                ('choice_one', models.CharField(max_length=250)),
                ('choice_two', models.CharField(max_length=250)),
            ],
        ),
    ]
