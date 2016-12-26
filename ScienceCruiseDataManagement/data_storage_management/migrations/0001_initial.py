# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 20:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Directories',
            },
        ),
        migrations.CreateModel(
            name='HardDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=255, unique=True)),
                ('label', models.CharField(max_length=255)),
                ('comment', models.TextField(blank=True, null=True)),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Person')),
            ],
        ),
        migrations.AddField(
            model_name='directory',
            name='hard_disk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_storage_management.HardDisk'),
        ),
    ]
