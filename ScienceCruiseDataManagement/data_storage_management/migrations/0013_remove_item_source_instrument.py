# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-05 13:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_storage_management', '0012_auto_20170303_1319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='source_instrument',
        ),
    ]