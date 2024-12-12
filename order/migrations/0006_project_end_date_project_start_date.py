# Generated by Django 5.1.3 on 2024-12-11 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_personproject_worklog'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='end_date',
            field=models.DateField(blank=True, help_text='Date when the project is expected to end.', null=True, verbose_name='End Date'),
        ),
        migrations.AddField(
            model_name='project',
            name='start_date',
            field=models.DateField(blank=True, help_text='Date when the project starts.', null=True, verbose_name='Start Date'),
        ),
    ]
