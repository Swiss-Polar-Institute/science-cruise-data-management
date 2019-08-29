# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-30 18:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0080_auto_20170825_1602'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='leg',
        ),
        migrations.RemoveField(
            model_name='person',
            name='onboard_role',
        ),
        migrations.RemoveField(
            model_name='person',
            name='principal_investigator',
        ),
        migrations.RemoveField(
            model_name='person',
            name='project',
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together=set([('name_first', 'name_last')]),
        ),
    ]
