# Generated by Django 5.1.4 on 2024-12-17 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personproject',
            name='assigned_at',
            field=models.DateTimeField(verbose_name='Assigned At'),
        ),
    ]
