# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-31 07:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_openevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailOversizeNotified',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_email', models.CharField(max_length=1024)),
                ('date_string', models.CharField(help_text='Date as it comes from the IMAP header', max_length=255)),
                ('size', models.IntegerField()),
                ('subject', models.CharField(max_length=1024)),
                ('imap_uuid', models.CharField(max_length=50)),
                ('to_email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Email')),
            ],
        ),
    ]
