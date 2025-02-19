# Generated by Django 5.1.3 on 2024-12-11 12:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eval', '0005_workday_assigned_hours_workday_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workday',
            name='assigned_hours',
            field=models.DurationField(default=datetime.timedelta(0), help_text='Total time for assigned hours.', verbose_name='Assigned Hours'),
        ),
        migrations.AlterField(
            model_name='workday',
            name='total_illegal_break',
            field=models.DurationField(default=datetime.timedelta(0), help_text='Total time for unauthorized breaks.', verbose_name='Total Illegal Break Hours'),
        ),
        migrations.AlterField(
            model_name='workday',
            name='total_legal_break',
            field=models.DurationField(default=datetime.timedelta(0), help_text='Total time for legal breaks.', verbose_name='Total Legal Break Hours'),
        ),
        migrations.AlterField(
            model_name='workday',
            name='total_work_hours',
            field=models.DurationField(help_text='Total work hours including breaks and working time.', verbose_name='Total Work Hours'),
        ),
    ]
