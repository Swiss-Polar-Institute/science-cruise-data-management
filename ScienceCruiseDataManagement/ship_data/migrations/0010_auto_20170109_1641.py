# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-09 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ship_data', '0009_auto_20170107_0629'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetDataFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('date_imported', models.DateTimeField(max_length=255)),
            ],
        ),
        migrations.RenameField(
            model_name='metdatawind',
            old_name='TIME',
            new_name='date_time',
        ),
        migrations.RemoveField(
            model_name='metdatawind',
            name='DAY',
        ),
        migrations.RemoveField(
            model_name='metdatawind',
            name='Month',
        ),
        migrations.RemoveField(
            model_name='metdatawind',
            name='Year',
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='CL1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='CL2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='CL3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='CLOUDTEXT',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='DP1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='DP2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='PA1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='PA2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='RH1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='RH2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='SC1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='SC2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='SC3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='SR1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='SR2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='SR3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='TA1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='TA2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='TIMEDIFF',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='TwTwTw',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='UV1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='UV2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='VIS',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='VISCODE',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD10MA1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD10MA2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD10MM1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD10MM2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD10MX1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD10MX2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD2MA1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD2MA2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD2MM1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD2MM2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD2MX1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WD2MX2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS10MA1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS10MA2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS10MM',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS10MM2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS10MX1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS10MX2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS2MA1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS2MA2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS2MM1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS2MM2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS2MX1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='WS2MX2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='cond',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='salinity',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='metdataall',
            name='wawa',
            field=models.FloatField(blank=True, null=True),
        ),
    ]