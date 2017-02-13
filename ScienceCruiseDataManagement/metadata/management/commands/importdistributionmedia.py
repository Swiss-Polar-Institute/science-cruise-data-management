from django.core.management.base import BaseCommand, CommandError
from metadata.models import DistributionMedia
import csv

class Command(BaseCommand):
    help = 'Adds data to the distribution media table.'

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
                distributionmedia = DistributionMedia()
                distributionmedia.media_type= row['media_type']
                distributionmedia.distribution_media= row['distribution_media']
                distributionmedia.download_date = row['download_date']

                distributionmedia.save()