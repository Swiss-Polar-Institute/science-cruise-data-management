# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-15 20:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_person_email_address'),
        ('metadata', '0010_auto_20170215_1943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distribution',
            name='distribution_format',
        ),
        migrations.AddField(
            model_name='distribution',
            name='distribution_format',
            field=models.ManyToManyField(blank=True, help_text='The data format used to distribute the data.', to='metadata.DistributionFormat'),
        ),
        migrations.RemoveField(
            model_name='personnel',
            name='contact_address',
        ),
        migrations.AddField(
            model_name='personnel',
            name='contact_address',
            field=models.ManyToManyField(blank=True, to='main.Organisation'),
        ),
    ]