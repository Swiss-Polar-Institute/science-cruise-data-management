# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-06 02:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_event_comments'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ctdcast',
            options={'verbose_name_plural': 'CTD casts'},
        ),
        migrations.AlterField(
            model_name='platform',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Country'),
        ),
    ]