# Generated by Django 5.1.3 on 2024-12-12 20:40

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agent', '0001_initial'),
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Date')),
                ('start_time', models.TimeField(blank=True, help_text='Time when the employee started work.', null=True, verbose_name='Start Time')),
                ('end_time', models.TimeField(blank=True, help_text='Time when the employee finished work.', null=True, verbose_name='End Time')),
                ('total_work_hours', models.DurationField(help_text='Total work hours including breaks and working time.', verbose_name='Total Work Hours')),
                ('total_legal_break', models.DurationField(default=datetime.timedelta(0), help_text='Total time for legal breaks.', verbose_name='Total Legal Break Hours')),
                ('total_illegal_break', models.DurationField(default=datetime.timedelta(0), help_text='Total time for unauthorized breaks.', verbose_name='Total Illegal Break Hours')),
                ('assigned_hours', models.DurationField(default=datetime.timedelta(0), help_text='Total time for assigned hours.', verbose_name='Assigned Hours')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agent.person', verbose_name='Employee')),
            ],
            options={
                'verbose_name': 'Work Day',
                'verbose_name_plural': 'Work Days',
                'unique_together': {('employee', 'date')},
            },
        ),
        migrations.CreateModel(
            name='WorkDayAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_hours', models.DecimalField(decimal_places=2, help_text='The number of hours assigned to this project.', max_digits=5, verbose_name='Assigned Hours')),
                ('work_performed', models.CharField(help_text='Description of the work performed.', max_length=100, verbose_name='Work Performed')),
                ('project', models.ForeignKey(help_text='The project to which the hours are assigned.', on_delete=django.db.models.deletion.CASCADE, to='order.project', verbose_name='Project')),
                ('workday', models.ForeignKey(help_text='The workday to which this assignment belongs.', on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='eval.workday', verbose_name='Work Day')),
            ],
            options={
                'verbose_name': 'Work Day Assignment',
                'verbose_name_plural': 'Work Day Assignments',
                'unique_together': {('workday', 'project')},
            },
        ),
    ]
