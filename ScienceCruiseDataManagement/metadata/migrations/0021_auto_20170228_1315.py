# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-28 13:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0020_auto_20170220_0233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metadataentry',
            name='distribution',
        ),
        migrations.AddField(
            model_name='distribution',
            name='metadata_entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='metadata.MetadataEntry'),
        ),
    ]
