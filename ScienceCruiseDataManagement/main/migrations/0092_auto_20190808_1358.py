# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2019-08-08 13:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0091_person_mailing_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='ship',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Ship'),
        ),
    ]