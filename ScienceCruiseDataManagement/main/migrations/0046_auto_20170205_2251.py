# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-05 22:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_island_island_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificdevice',
            name='calibration_comments',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='specificdevice',
            name='calibration_documents',
            field=models.BooleanField(default=0, help_text='Select this box if this device should be calibrated and the calibration documents are in the data folder.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='specificdevice',
            name='calibration_required',
            field=models.BooleanField(default=0, help_text='Select this box if this device should be calibrated.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='specificdevice',
            name='device_comments',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
