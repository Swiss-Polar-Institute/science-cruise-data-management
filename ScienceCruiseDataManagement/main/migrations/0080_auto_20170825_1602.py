# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-25 16:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0079_auto_20170825_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Organisation'),
        ),
    ]