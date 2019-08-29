# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-03 10:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_auto_20170202_0656'),
    ]

    operations = [
        migrations.CreateModel(
            name='TmrCast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmr_cast_number', models.IntegerField()),
                ('event_number', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.Event')),
                ('leg_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Leg')),
            ],
        ),
        migrations.AlterField(
            model_name='device',
            name='main_device_type',
            field=models.ManyToManyField(blank=True, help_text='Select one or more options of available, from this list of controlled vocabulary devices. If there is nothing suitable, do not select anything. Note that there are some very specific devices and other more general categories, all of which should be selected if they are correct.', related_name='device_type', to='main.DeviceType'),
        ),
        migrations.AlterField(
            model_name='specificdevice',
            name='possible_parent',
            field=models.ManyToManyField(blank=True, help_text='If the device is deployed by attaching it to another instrument, then it has a parent: enter this device here. Some devices may have more than one parent device, for example if the parent device breaks and is swapped.', to='main.SpecificDevice'),
        ),
        migrations.AlterUniqueTogether(
            name='tmrcast',
            unique_together=set([('tmr_cast_number', 'leg_number')]),
        ),
    ]
