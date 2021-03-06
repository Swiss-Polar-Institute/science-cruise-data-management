# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 05:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_organisation_city'),
        ('metadata', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasetprogress',
            options={'verbose_name_plural': 'Dataset progress'},
        ),
        migrations.AlterModelOptions(
            name='metadataentry',
            options={'verbose_name_plural': 'Metadata entries'},
        ),
        migrations.AlterModelOptions(
            name='personnel',
            options={'verbose_name_plural': 'Personnel'},
        ),
        migrations.AlterModelOptions(
            name='summary',
            options={'verbose_name_plural': 'Summaries'},
        ),
        migrations.AlterField(
            model_name='datacenter',
            name='data_set_id',
            field=models.CharField(blank=True, help_text='This is a data set identifier assigned by the data center (may or may not be the same as the <Entry_ID>.', max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='horizontalresolutionrange',
            name='horizontal_resolution_range',
            field=models.CharField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='horizontalresolutionrange',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='instrument',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='metadataentry',
            name='dif_creation_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metadataentry',
            name='future_dif_review_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metadataentry',
            name='last_dif_revision_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metadataentry',
            name='metadata_version',
            field=models.CharField(default='TEST', help_text='DEFAULT=VERSION 9.9', max_length=80),
        ),
        migrations.AlterField(
            model_name='metadataentry',
            name='private',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parameter',
            name='download_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='keyword_revision_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='platform',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rucontenttype',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='easternmost_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='maximum_altitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='maximum_depth',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='minimum_altitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='minimum_depth',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='northernmost_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='southernmost_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spatialcoverage',
            name='westernmost_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='temporalresolutionrange',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='verticalresolutionrange',
            name='uuid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='datasetcitation',
            unique_together=set([('dataset_creator', 'dataset_title')]),
        ),
        migrations.AlterUniqueTogether(
            name='instrument',
            unique_together=set([('category', 'instrument_class', 'type', 'subtype', 'short_name', 'long_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([('location_category', 'location_type', 'location_subregion1', 'location_subregion2', 'location_subregion3')]),
        ),
        migrations.AlterUniqueTogether(
            name='parameter',
            unique_together=set([('category', 'topic', 'term', 'variable_level_1', 'variable_level_2', 'variable_level_3', 'detailed_variable')]),
        ),
        migrations.AlterUniqueTogether(
            name='platform',
            unique_together=set([('category', 'series_entity', 'short_name', 'long_name')]),
        ),
    ]
