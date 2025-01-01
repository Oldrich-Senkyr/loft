# Generated by Django 5.1.4 on 2024-12-31 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='unique_id',
            field=models.CharField(help_text='Enter a unique identifier.', max_length=20, unique=True, verbose_name='Unique ID'),
        ),
    ]
