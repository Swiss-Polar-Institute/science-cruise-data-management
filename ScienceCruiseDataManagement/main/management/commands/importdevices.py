from django.core.management.base import BaseCommand, CommandError
from main.models import DeviceType
import os
import csv
import codecs
import glob
from main import utils
import io

class Command(BaseCommand):
    help = 'Adds data to the ChildDevice table'

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
        with codecs.open(io.StringIO(utils.normalised_csv_file(filepath)), encoding = 'utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                device_type = DeviceType()
                device_type.url = row['Url']
                device_type.code = row['Identifier']
                device_type.name = row['PrefLabel']
                device_type.description = row['Definition']
                device_type.version = row['Version']

                device_type.date = row['Date']

                # Set the source for the record according to the filename.
                basename = os.path.basename(filepath)
                filename = os.path.splitext(basename)[0]

                device_type.source = filename.split('_')[-1]

                device_type.deprecated = row['Deprecated']
                device_type.save()

