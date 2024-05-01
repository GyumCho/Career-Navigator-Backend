# Generated by Django 5.0.2 on 2024-04-18 13:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0016_delete_questionresult'),
    ]

    database_operations = []

    state_operations = [
        migrations.CreateModel(
            name='QuestionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('MbtiType', models.CharField(default='', max_length=250)),
                ('codeOne', models.CharField(default='', max_length=250)),
                ('codeTwo', models.CharField(blank=True, default='', max_length=250)),
                ('category_one', models.CharField(default='', max_length=250)),
                ('category_two', models.CharField(default='', max_length=250)),
                ('category_three', models.CharField(default='', max_length=250)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(database_operations, state_operations)
    ]
