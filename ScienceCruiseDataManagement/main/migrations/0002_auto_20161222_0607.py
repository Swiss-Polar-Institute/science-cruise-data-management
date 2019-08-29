# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 06:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PositionSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('definition', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimeSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('definition', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='person',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='child_devices',
            field=smart_selects.db_fields.ChainedManyToManyField(blank=True, chained_field='parent_device', chained_model_field='possible_parents', to='main.ChildDevice'),
        ),
        migrations.AlterField(
            model_name='event',
            name='station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Station'),
        ),
        migrations.AlterField(
            model_name='eventaction',
            name='event',
            field=models.ForeignKey(help_text='Select the event for which you want to enter an action.', on_delete=django.db.models.deletion.CASCADE, to='main.Event'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='parentdevice',
            name='definition',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]