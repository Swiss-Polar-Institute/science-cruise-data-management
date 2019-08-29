# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-30 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expedition_reporting', '0003_auto_20170930_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreachactivity',
            name='project',
            field=models.ManyToManyField(blank=True, help_text='Please select the project(s) to which your outreach activity was related. If it was about the expedition in general, please select all projects.', to='main.Project'),
        ),
    ]
