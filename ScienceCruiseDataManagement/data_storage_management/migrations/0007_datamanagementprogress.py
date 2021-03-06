# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 07:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_samplefile'),
        ('data_storage_management', '0006_auto_20170105_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataManagementProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_recording', models.CharField(choices=[('Complete', 'Complete'), ('In progress', 'In progress'), ('Not started', 'Not started')], max_length=255)),
                ('events_complete', models.BooleanField()),
                ('sample_recording', models.CharField(choices=[('Complete', 'Complete'), ('In progress', 'In progress'), ('Not started', 'Not started')], max_length=255)),
                ('samples_complete', models.BooleanField()),
                ('metadata_record', models.CharField(choices=[('Complete', 'Complete'), ('In progress', 'In progress'), ('Not started', 'Not started')], max_length=255)),
                ('data_management_plan', models.CharField(choices=[('Complete', 'Complete'), ('In progress', 'In progress'), ('Not started', 'Not started')], max_length=255)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('data_contact', models.ManyToManyField(to='main.Person')),
                ('leg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Leg')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Project')),
            ],
        ),
    ]
