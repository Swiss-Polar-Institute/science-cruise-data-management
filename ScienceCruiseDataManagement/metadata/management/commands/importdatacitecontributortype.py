from django.core.management.base import BaseCommand, CommandError
from metadata.models import DataciteContributorType
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Adds data to the datacite contributor type table.'

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
                datacitecontributortype = DataciteContributorType()
                datacitecontributortype.contributor_type = row['CONTRIBUTOR_TYPE']
                datacitecontributortype.datacite_schema_version = row['DATACITE_SCHEMA_VERSION']
                datacitecontributortype.in_datacite = settings.DEFAULT_IN_DATACITE

                datacitecontributortype.save()