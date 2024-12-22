# Generated by Django 5.1.4 on 2024-12-22 09:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0004_remove_person_company_alter_person_managed_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='managed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persons', to='agent.userhierarchynode', verbose_name='Managed by'),
        ),
    ]
