# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-03 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_samplingmethod_directory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='number',
            field=models.IntegerField(unique=True),
        ),
    ]
