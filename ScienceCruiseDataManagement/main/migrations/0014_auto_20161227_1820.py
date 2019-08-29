# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-27 18:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20161227_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventaction',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='TIME IN UTC', verbose_name='Time of event action (UTC)'),
        ),
    ]
