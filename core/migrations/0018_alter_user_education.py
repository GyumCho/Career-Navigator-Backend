# Generated by Django 5.0.2 on 2024-04-04 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_user_education'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='education',
            field=models.JSONField(default=list, verbose_name='Education'),
        ),
    ]