# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-17 22:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0070_auto_20170313_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='comments',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
