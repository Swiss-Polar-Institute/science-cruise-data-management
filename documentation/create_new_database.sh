To delete the database (with all its contents) and create a new one do:

rm -rf main/migrations
rm -rf data_storage_management/migrations/
rm -rf ship_data/migrations/
rm -rf ctd/migrations/
rm -rf metadata/migrations/
rm -rf underway_sampling/migrations/

# Careful next line will delete all the database!
# echo "drop database ace2016; create database ace2016;" | python3 manage.py dbshell

python3 manage.py makemigrations data_storage_management main ship_data ctd metadata underway_sampling

python3 manage.py migrate

python3 manage.py createsuperuser

python3 manage.py importall ~/tables_to_upload
