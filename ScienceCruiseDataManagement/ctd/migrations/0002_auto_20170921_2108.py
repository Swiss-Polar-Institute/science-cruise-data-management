# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-21 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0084_auto_20170921_1427'),
        ('ctd', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ctdvariable',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ctdvariable',
            name='principal_investigator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Person'),
        ),
    ]