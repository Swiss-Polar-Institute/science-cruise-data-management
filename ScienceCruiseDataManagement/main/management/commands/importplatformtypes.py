from django.core.management.base import BaseCommand, CommandError
from main.models import PlatformType
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
                platformtype = PlatformType()
                platformtype.url = row['Url']
                platformtype.code = row['Identifier']
                platformtype.name = row['PrefLabel']
                platformtype.definition = row['Definition']
                platformtype.version = row['Version']
                platformtype.deprecated = row['Deprecated']
                platformtype.date = row['Date']
                platformtype.source = row['source']

                platformtype.save()

