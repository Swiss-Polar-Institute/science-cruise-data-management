# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-22 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctd', '0004_auto_20170922_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ctdvariable',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
