# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-05 23:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20170205_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
