# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_specificdevice_sampling_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='sampling_methods',
            field=models.ManyToManyField(to='main.SamplingMethod'),
        ),
    ]
