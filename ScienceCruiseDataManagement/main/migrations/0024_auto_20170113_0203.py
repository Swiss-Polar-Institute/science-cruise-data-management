# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-13 02:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_samplefile'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_changed_utc', models.DateField()),
                ('difference_to_utc_after_change', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='sample',
            name='file',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
