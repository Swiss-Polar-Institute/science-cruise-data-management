from django.core.management.base import BaseCommand, CommandError
from main.models import Organisation, Country
import csv

class Command(BaseCommand):
    help = 'Adds data to the person table'

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
                organisation = Organisation()
                organisation.name = row['name']
                organisation.address = row['address']

                if row['country'] != '':
                    country = Country.objects.filter(name=row['country'])[0]
                    organisation.country = country

                organisation.save()

