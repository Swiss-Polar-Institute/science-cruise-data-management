# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-06 00:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_event_comments'),
        ('data_storage_management', '0007_datamanagementprogress'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='source_instrument',
            field=models.ManyToManyField(blank=True, help_text='Select the instrument(s) which produced the data in this folder.', null=True, to='main.SpecificDevice'),
        ),
    ]
