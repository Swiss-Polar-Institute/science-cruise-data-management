# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0021_auto_20170228_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadataentry',
            name='skip_update_distribution_size',
            field=models.BooleanField(default=False),
        ),
    ]
