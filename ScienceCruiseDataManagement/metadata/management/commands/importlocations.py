from django.core.management.base import BaseCommand, CommandError
from metadata.models import Location
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Adds data to the location table.'

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
                location = Location()
                location.location_category = row['Location_Category']
                location.location_type = row['Location_Type']
                location.location_subregion1= row['Location_Subregion1']
                location.location_subregion2 = row['Location_Subregion2']
                location.location_subregion3= row['Location_Subregion3']
                location.detailed_location = row['Detailed_Location']
                location.uuid = row['UUID']
                location.keyword_version = row['keyword_version']
                location.keyword_revision_date = row['keyword_revision_date']
                location.download_date = row['download_date']
                location.in_gcmd = settings.DEFAULT_IN_GCMD

                location.save()