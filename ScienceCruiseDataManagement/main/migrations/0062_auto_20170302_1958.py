# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-02 19:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_storage_management', '0011_item_path_storage'),
        ('main', '0061_auto_20170302_1245'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificdevice',
            name='directory',
            field=models.ManyToManyField(blank=True, to='data_storage_management.Item'),
        ),
        migrations.AlterField(
            model_name='project',
            name='number',
            field=models.CharField(max_length=3, unique=True),
        ),
    ]
