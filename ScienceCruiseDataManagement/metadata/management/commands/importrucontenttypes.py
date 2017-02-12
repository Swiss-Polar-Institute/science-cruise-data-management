from django.core.management.base import BaseCommand, CommandError
from metadata.models import RUContentType
import csv

class Command(BaseCommand):
    help = 'Adds data to the related url content type table.'

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
                rucontenttype = RUContentType()
                rucontenttype.type = row['Type']
                rucontenttype.subtype = row['Subtype']
                rucontenttype.uuid = ['UUID']
                rucontenttype.keyword_version = row['keyword_version']
                rucontenttype.keyword_revision_date = row['keyword_revision_date']
                rucontenttype.download_date = row['download_date']

                rucontenttype.save()