# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-04 04:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_onboardrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='onboard_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.OnboardRole'),
        ),
        migrations.RemoveField(
            model_name='person',
            name='project',
        ),
        migrations.AddField(
            model_name='person',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Project'),
        ),
    ]