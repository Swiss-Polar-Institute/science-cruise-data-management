# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2019-08-08 15:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ship_data', '0020_cruisetrack'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cruisetrack',
            old_name='device_id',
            new_name='device',
        ),
    ]
