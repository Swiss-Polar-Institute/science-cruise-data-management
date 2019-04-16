#!/bin/bash

echo "drop database glace; create database glace;" | python3 manage.py dbshell

rm -rf main/migrations/
rm -rf ship_data/migrations/
rm -rf data_storage_management/migrations/
rm -rf ctd/migrations/
rm -rf underway_sampling/migrations/
rm -rf metadata/migrations/
rm -rf data_administration/migrations/
rm -rf data_management/migrations/
rm -rf data_storage_management/migrations/
rm -rf spi_admin/migrations/

python3 manage.py makemigrations metadata ship_data data_storage_management ctd underway_sampling main expedition_reporting data_administration data_management spi_admin
python3 manage.py migrate 

echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
