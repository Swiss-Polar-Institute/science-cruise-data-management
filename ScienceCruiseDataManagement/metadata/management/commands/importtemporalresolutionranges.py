from django.core.management.base import BaseCommand, CommandError
from metadata.models import TemporalResolutionRange
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Adds data to the temporal resolution range table.'

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
                temporalresolutionrange = TemporalResolutionRange()
                temporalresolutionrange.temporal_resolution_range = row['Temporal_Resolution_Range']
                temporalresolutionrange.uuid = row['UUID']
                temporalresolutionrange.keyword_version = row['keyword_version']
                temporalresolutionrange.keyword_revision_date = row['keyword_revision_date']
                temporalresolutionrange.download_date= row['download_date']
                temporalresolutionrange.in_gcmd = settings.DEFAULT_IN_GCMD

                temporalresolutionrange.save()