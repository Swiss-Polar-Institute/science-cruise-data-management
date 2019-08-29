# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 15:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20161227_1841'),
        ('ship_data', '0003_auto_20161226_0751'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpggagpsfix',
            name='device',
            field=models.ForeignKey(default=63, on_delete=django.db.models.deletion.CASCADE, to='main.SamplingMethod'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gpvtgvelocity',
            name='device',
            field=models.ForeignKey(default=63, on_delete=django.db.models.deletion.CASCADE, to='main.SamplingMethod'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gpzdadatetime',
            name='device',
            field=models.ForeignKey(default=63, on_delete=django.db.models.deletion.CASCADE, to='main.SamplingMethod'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gpggagpsfix',
            name='geoid_height',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gpggagpsfix',
            name='geoid_height_units',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='gpvtgvelocity',
            name='magnetic_track_deg',
            field=models.FloatField(blank=True, null=True),
        ),
    ]