# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-19 15:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0016_auto_20170219_1419'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='datasetcitation',
            unique_together=set([]),
        ),
    ]
