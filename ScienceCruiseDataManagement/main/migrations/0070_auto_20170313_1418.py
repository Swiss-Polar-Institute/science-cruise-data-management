# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-13 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0069_auto_20170311_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsconsistencyv2',
            name='event_from_project_code',
            field=models.IntegerField(),
        ),
    ]