from django.core.management.base import BaseCommand, CommandError
from main.models import Platform, PlatformType, Country
import csv

class Command(BaseCommand):
    help = 'Adds data to the platform table'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'])

    def import_data_from_csv(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                platform = Platform()
                platform.url = row['Url']
                platform.code = row['Identifier']
                platform.name = row['PrefLabel']

                if row['country'] != '':
                    country = Country.objects.all().filter(name=row['country'])[0]
                    platform.country = country

                if row['platformtype'] != '':
                    platformtype = PlatformType.objects.all().filter(name=row['platformtype'])[0]
                    platform.platformtype = platformtype

                platform.source = row['source']

                platform.save()

