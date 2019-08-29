# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 11:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_auto_20170301_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificdevice',
            name='sampling_method',
            field=models.ForeignKey(blank=True, help_text='Link each device to a sampling method so that the data can be linked to events.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sampling_method_device', to='main.SamplingMethod'),
        ),
    ]
