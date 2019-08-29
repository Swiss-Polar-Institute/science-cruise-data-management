# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-02 06:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_ctdcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ctdcast',
            name='event_number',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.Event'),
        ),
        migrations.AlterUniqueTogether(
            name='ctdcast',
            unique_together=set([('ctd_cast_number', 'leg_number')]),
        ),
    ]
