# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-21 09:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0082_auto_20170904_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='timechange',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='timechange',
            name='data_source',
            field=models.CharField(default='data manager', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timechange',
            name='date_changed_ship_time',
            field=models.DateField(blank=True, null=True),
        ),
    ]
