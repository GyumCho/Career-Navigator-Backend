# Generated by Django 5.0.2 on 2024-03-20 10:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_rename_owner_jobbookmarks_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobbookmarks",
            name="job",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, to="core.job"
            ),
        ),
    ]
