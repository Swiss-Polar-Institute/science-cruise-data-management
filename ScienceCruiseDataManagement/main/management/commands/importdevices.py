from django.core.management.base import BaseCommand, CommandError
from main.models import Device
import os
import csv
import codecs
import glob

class Command(BaseCommand):
    help = 'Adds data to the device table'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', type=str)

    def handle(self, *args, **options):
        print(options['directory_name'])
        self.import_data_from_directory(options['directory_name'])

    def import_data_from_directory(self, directory_name):
        for file in glob.glob(directory_name+"/device*.csv"):
            print(directory_name+"/device*.csv")
            self.import_data_from_csv(file)

    def import_data_from_csv(self, filepath):
        with codecs.open(filepath, encoding = 'utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                device = Device()
                device.url = row['Url']
                device.code = row['Identifier']
                device.name = row['PrefLabel']
                device.description = row['Definition']
                device.version = row['Version']

                device.date = row['Date']

                # Set the source for the record according to the filename.
                basename = os.path.basename(filepath)
                filename = os.path.splitext(basename)[0]

                device.source = filename.split('_')[-1]

                device.deprecated = row['Deprecated']
                device.save()

