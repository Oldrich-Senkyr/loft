# Generated by Django 5.1.3 on 2024-11-24 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0008_alter_attendanceevent_departure_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceevent',
            name='departure_reason',
            field=models.IntegerField(blank=True, choices=[(0, 'N/a'), (1, 'Legal'), (2, 'Illegal')], default=0),
        ),
    ]
