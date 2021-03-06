# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-07 06:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ship_data', '0008_metdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetDataWind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TIME', models.DateTimeField(unique=True, verbose_name='Date time')),
                ('COG', models.FloatField(blank=True, null=True, verbose_name='Course over ground')),
                ('HEADING', models.FloatField(blank=True, null=True, verbose_name='Heading')),
                ('WDR1', models.FloatField(blank=True, null=True, verbose_name='Relative wind direction 1')),
                ('WSR1', models.FloatField(blank=True, null=True, verbose_name='Relative wind speed 1')),
                ('WD1', models.FloatField(blank=True, null=True, verbose_name='Wind direction 1')),
                ('WS1', models.FloatField(blank=True, null=True, verbose_name='Wind speed 1')),
                ('WDR2', models.FloatField(blank=True, null=True, verbose_name='Relative wind direction 2')),
                ('WSR2', models.FloatField(blank=True, null=True, verbose_name='Relative wind speed 2')),
                ('WD2', models.FloatField(blank=True, null=True, verbose_name='Wind direction 2')),
                ('WS2', models.FloatField(blank=True, null=True, verbose_name='Wind speed 2')),
                ('TIMEDIFF', models.FloatField(blank=True, null=True, verbose_name='Time difference')),
                ('Year', models.IntegerField(blank=True, null=True)),
                ('Month', models.IntegerField(blank=True, null=True)),
                ('DAY', models.IntegerField(blank=True, null=True)),
                ('CLOUDTEXT', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Meterological data - wind',
            },
        ),
        migrations.RenameModel(
            old_name='MetData',
            new_name='MetDataAll',
        ),
        migrations.AlterModelOptions(
            name='metdataall',
            options={'verbose_name_plural': 'Meterological data - full set'},
        ),
    ]
