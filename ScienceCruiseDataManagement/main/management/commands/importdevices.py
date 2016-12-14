from django.core.management.base import BaseCommand, CommandError
from main.models import Device
import csv

class Command(BaseCommand):
    help = 'Adds data to the device table'

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
                device = Device()
                device.url = row['url']
                device.code = row['code']
                device.name = row['name']
                device.description = row['definition']
                device.version = row['version']

                device.date = row['date']
                device.source = row['source']

                device.deprecated = row['deprecated']
                device.save()

