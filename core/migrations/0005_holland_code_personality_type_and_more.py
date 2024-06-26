# Generated by Django 5.0.2 on 2024-03-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_jobs'),
    ]

    operations = [
        migrations.CreateModel(
            name='holland_code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='personality_type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='jobs',
            name='education_one',
            field=models.CharField(max_length=150, verbose_name='education_one'),
        ),
        migrations.AlterField(
            model_name='jobs',
            name='education_three',
            field=models.CharField(max_length=150, verbose_name='education_three'),
        ),
        migrations.AlterField(
            model_name='jobs',
            name='education_two',
            field=models.CharField(max_length=150, verbose_name='education_two'),
        ),
        migrations.RemoveField(
            model_name='jobs',
            name='holland_code',
        ),
        migrations.AlterField(
            model_name='jobs',
            name='job_name',
            field=models.CharField(max_length=150, verbose_name='job_name'),
        ),
        migrations.RemoveField(
            model_name='jobs',
            name='personality_type',
        ),
        migrations.AddField(
            model_name='jobs',
            name='holland_code',
            field=models.ManyToManyField(blank=True, to='core.holland_code'),
        ),
        migrations.AddField(
            model_name='jobs',
            name='personality_type',
            field=models.ManyToManyField(blank=True, to='core.personality_type'),
        ),
    ]
