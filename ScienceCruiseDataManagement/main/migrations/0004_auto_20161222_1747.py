# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 17:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20161222_0641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
