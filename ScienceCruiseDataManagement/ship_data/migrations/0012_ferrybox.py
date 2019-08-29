# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-12 02:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ship_data', '0011_auto_20170117_1402'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ferrybox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('salinity', models.FloatField()),
                ('conductivity', models.FloatField()),
                ('temperature', models.FloatField()),
            ],
            options={
                'get_latest_by': 'date_time',
            },
        ),
    ]
