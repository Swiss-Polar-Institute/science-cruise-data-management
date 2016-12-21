from django.core.management.base import BaseCommand, CommandError
from main.models import ParentDevice
import csv

class Command(BaseCommand):
    help = 'Adds data to the parent device table'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'])

    def import_data_from_csv(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                parent_device = ParentDevice()
                parent_device.name = row['name']
                parent_device.definition = row['definition']

                parent_device.save()

