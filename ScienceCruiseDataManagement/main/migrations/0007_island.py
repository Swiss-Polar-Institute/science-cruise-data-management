# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-26 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20161223_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='Island',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('mid_lat', models.FloatField(blank=True, null=True)),
                ('mid_lon', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
