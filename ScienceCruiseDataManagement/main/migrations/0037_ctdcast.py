# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-02 06:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20170201_2333'),
    ]

    operations = [
        migrations.CreateModel(
            name='CtdCast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ctd_cast_number', models.IntegerField()),
                ('ctd_file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('ice_coverage', models.CharField(blank=True, max_length=255, null=True)),
                ('sea_state', models.CharField(blank=True, max_length=255, null=True)),
                ('water_depth', models.FloatField(blank=True, null=True)),
                ('surface_temperature', models.FloatField(blank=True, null=True)),
                ('surface_salinity', models.FloatField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('ctd_operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Person')),
                ('event_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Event')),
                ('leg_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Leg')),
            ],
        ),
    ]