# Generated by Django 5.1.3 on 2024-12-10 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eval', '0004_alter_workdayassignment_project_delete_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='workday',
            name='assigned_hours',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Total time Assigned hours.', max_digits=5, verbose_name='Assigned hours'),
        ),
        migrations.AddField(
            model_name='workday',
            name='end_time',
            field=models.TimeField(blank=True, help_text='Time when the employee finished work.', null=True, verbose_name='End Time'),
        ),
        migrations.AddField(
            model_name='workday',
            name='start_time',
            field=models.TimeField(blank=True, help_text='Time when the employee started work.', null=True, verbose_name='Start Time'),
        ),
    ]
