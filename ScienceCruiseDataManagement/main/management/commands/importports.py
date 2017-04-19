from django.core.management.base import BaseCommand, CommandError
from main.models import Port, Country, settings
import csv

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

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
                    country = Country.objects.filter(name=row['country'])[0]
                    port.country = country

                port.latitude = row['latitude']
                port.longitude = row['longitude']
                port.version = row['Version']
                port.deprecated = row['Deprecated']
                port.date = row['Date']
                port.source = row['source']

                port.save()

