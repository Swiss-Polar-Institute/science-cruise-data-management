# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 18:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0015_auto_20161227_1841'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectoryUpdates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'Directory Updates',
            },
        ),
        migrations.CreateModel(
            name='HardDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=255, unique=True)),
                ('label', models.CharField(max_length=255, null=True)),
                ('added_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.TextField(blank=True, null=True)),
                ('person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_directory', models.CharField(max_length=255)),
                ('destination_directory', models.CharField(max_length=255, unique=True)),
                ('created_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('added_date_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='NASResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shared_resource', models.CharField(max_length=255, unique=True)),
                ('added_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'NAS Directories',
            },
        ),
        migrations.CreateModel(
            name='SharedResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('shared_resource', models.CharField(max_length=255)),
                ('added_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data_storage_management.Item')),
            ],
            options={
                'verbose_name_plural': 'Directories',
            },
            bases=('data_storage_management.item',),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data_storage_management.Item')),
            ],
            bases=('data_storage_management.item',),
        ),
        migrations.AddField(
            model_name='item',
            name='hard_disk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data_storage_management.HardDisk'),
        ),
        migrations.AddField(
            model_name='item',
            name='nas_resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data_storage_management.NASResource'),
        ),
        migrations.AddField(
            model_name='item',
            name='shared_resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data_storage_management.SharedResource'),
        ),
        migrations.AlterUniqueTogether(
            name='sharedresource',
            unique_together=set([('ip', 'shared_resource')]),
        ),
        migrations.AddField(
            model_name='directoryupdates',
            name='directory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_storage_management.Directory'),
        ),
    ]
