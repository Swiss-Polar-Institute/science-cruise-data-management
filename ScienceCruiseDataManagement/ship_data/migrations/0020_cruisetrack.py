# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2019-08-08 13:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0092_auto_20190808_1358'),
        ('ship_data', '0019_auto_20170921_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='CruiseTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(unique=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('fix_quality', models.IntegerField(blank=True, null=True)),
                ('number_satellites', models.IntegerField(blank=True, null=True)),
                ('horiz_dilution_of_position', models.FloatField(blank=True, null=True)),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('altitude_units', models.CharField(blank=True, max_length=1, null=True)),
                ('geoid_height', models.FloatField(blank=True, null=True)),
                ('geoid_height_units', models.CharField(blank=True, max_length=1, null=True)),
                ('speed', models.FloatField(blank=True, null=True)),
                ('measureland_qualifier_flag_overall', models.IntegerField(blank=True, null=True)),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.SamplingMethod')),
            ],
            options={
                'verbose_name_plural': 'Quality-checked cruise track',
            },
        ),
    ]