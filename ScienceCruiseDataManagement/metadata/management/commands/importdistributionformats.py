from django.core.management.base import BaseCommand, CommandError
from metadata.models import DistributionFormat
from django.conf import settings
import csv


class Command(BaseCommand):
    help = 'Adds data to the distribution format table.'

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
                distributionformat = DistributionFormat()
                distributionformat.distribution_format = row['distribution_format']
                distributionformat.description= row['description']
                distributionformat.download_date = row['download_date']
                distributionformat.in_gcmd = settings.DEFAULT_IN_GCMD

                distributionformat.save()