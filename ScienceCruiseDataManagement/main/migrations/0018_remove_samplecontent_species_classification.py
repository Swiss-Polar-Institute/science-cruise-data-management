# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 07:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20170102_1657'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='samplecontent',
            name='species_classification',
        ),
    ]