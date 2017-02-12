from django.core.management.base import BaseCommand, CommandError
from metadata.models import VerticalResolutionRange
import csv

class Command(BaseCommand):
    help = 'Adds data to the vertical resolution range table.'

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
                verticalresolutionrange = VerticalResolutionRange()
                verticalresolutionrange.vertical_resolution_range = row['Vertical_Resolution_Range']
                verticalresolutionrange.uuid = ['UUID']
                verticalresolutionrange.keyword_version = row['keyword_version']
                verticalresolutionrange.keyword_revision_date = row['keyword_revision_date']
                verticalresolutionrange.download_date= row['download_date']

                verticalresolutionrange.save()