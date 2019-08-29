# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-15 03:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20170213_2057'),
        ('metadata', '0005_auto_20170214_2201'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadataentry',
            name='expedition_specific_device',
            field=models.ManyToManyField(blank=True, to='main.SpecificDevice'),
        ),
        migrations.AlterField(
            model_name='distributionformat',
            name='distribution_format',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='distributionformat',
            unique_together=set([('distribution_format', 'description')]),
        ),
    ]
