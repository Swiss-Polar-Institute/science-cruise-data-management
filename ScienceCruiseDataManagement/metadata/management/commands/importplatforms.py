from django.core.management.base import BaseCommand, CommandError
from metadata.models import Platform
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Adds data to the platform table.'

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
                platform = Platform()
                platform.category = row['Category']
                platform.series_entity = row['Series_Entity']
                platform.short_name = row['Short_Name']
                platform.long_name = row['Long_Name']
                platform.uuid = row['UUID']
                platform.keyword_version = row['keyword_version']
                platform.keyword_revision_date = row['keyword_revision_date']
                platform.download_date = ['download_date']
                platform.in_gcmd = settings.DEFAULT_IN_GCMD

                platform.save()