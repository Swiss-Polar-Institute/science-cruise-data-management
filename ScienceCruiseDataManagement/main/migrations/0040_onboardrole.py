# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-04 03:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_auto_20170203_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
    ]