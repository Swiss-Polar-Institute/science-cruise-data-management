# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-21 09:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0074_station_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='station',
            name='description',
        ),
    ]
