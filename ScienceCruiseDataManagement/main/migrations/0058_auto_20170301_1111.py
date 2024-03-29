# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 11:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_auto_20170228_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificdevice',
            name='full_name',
            field=models.CharField(blank=True, help_text='Full name of the device as it is known.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='specificdevice',
            name='shortened_name',
            field=models.CharField(blank=True, help_text='Shortened name or acronym of the device by which it is known.', max_length=255, null=True),
        ),
    ]
