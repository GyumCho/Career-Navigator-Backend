# Generated by Django 5.0.2 on 2024-04-11 13:25

import martor.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_rename__address_contact_address_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='contact',
        ),
        migrations.DeleteModel(
            name='Education',
        ),
        migrations.DeleteModel(
            name='Work_Experience',
        ),
        migrations.AddField(
            model_name='company',
            name='description',
            field=martor.models.MartorField(default='', max_length=500),
            preserve_default=False,
        ),
    ]
