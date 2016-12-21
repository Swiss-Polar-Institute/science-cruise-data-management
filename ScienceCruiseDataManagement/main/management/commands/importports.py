from django.core.management.base import BaseCommand, CommandError
from main.models import Port, Country, settings
import csv

class Command(BaseCommand):
    help = 'Adds data to the port table'

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
                port = Port()
                port.url = row['Url']
                port.code = row['Identifier']
                port.name = row['PrefLabel']

                if row['country'] != '':
                    country = Country.objects.all().filter(name=row['country'])[0]
                    port.country = country

                port.latitude = row['latitude']
                port.longitude = row['longitude']
                port.version = row['Version']
                port.deprecated = row['Deprecated']
                port.date = row['Date']
                port.source = row['source']

                port.save()

