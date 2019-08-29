# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-28 02:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0056_depth'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='depth',
            options={'get_latest_by': 'date_time'},
        ),
        migrations.AlterField(
            model_name='emailoversizenotified',
            name='date_string',
            field=models.CharField(help_text='Date as it comes from the IMAP header', max_length=255, null=True),
        ),
    ]
