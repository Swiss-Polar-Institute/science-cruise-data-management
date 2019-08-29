# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 13:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_storage_management', '0010_auto_20170209_0751'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='path_storage',
            field=models.CharField(blank=True, help_text='If the file/directory are saved in a specific place instead of the standard place', max_length=255, null=True),
        ),
    ]