# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 20:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_organisation_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specificdevice',
            name='project',
            field=models.ManyToManyField(help_text='Select the templates which used the device or got samples / data from its deployments.', to='main.Project'),
        ),
    ]