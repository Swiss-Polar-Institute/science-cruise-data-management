# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-05 05:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_specificdevice_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='island',
            name='island_group',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]