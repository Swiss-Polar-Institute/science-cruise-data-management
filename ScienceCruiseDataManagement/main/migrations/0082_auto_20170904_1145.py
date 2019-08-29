# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-04 11:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0081_auto_20170830_1832'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OnboardRole',
            new_name='Role',
        ),
        migrations.RenameField(
            model_name='personrole',
            old_name='onboard_role',
            new_name='role',
        ),
        migrations.AlterUniqueTogether(
            name='personrole',
            unique_together=set([('person', 'project', 'role')]),
        ),
    ]