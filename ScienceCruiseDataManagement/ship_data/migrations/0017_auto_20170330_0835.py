# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-30 08:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ship_data', '0016_multibeamrawfilemetadata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='multibeamrawfilemetadata',
            old_name='file_end_time_iso',
            new_name='file_end_time',
        ),
        migrations.RenameField(
            model_name='multibeamrawfilemetadata',
            old_name='file_start_time_iso',
            new_name='file_start_time',
        ),
    ]
