# Generated by Django 5.0.2 on 2024-03-27 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_interest_holland_question_holland'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question_mbti',
            old_name='question_fix',
            new_name='question',
        ),
    ]