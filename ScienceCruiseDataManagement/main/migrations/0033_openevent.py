# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-29 04:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20170127_0818'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenEvent',
            fields=[
                ('number', models.IntegerField(help_text='Event number that is opened', primary_key=True, serialize=False, unique=True)),
            ],
        ),
    ]
