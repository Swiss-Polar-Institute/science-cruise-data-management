from django.core.management.base import BaseCommand, CommandError
from metadata.models import Project
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
                project = Project()
                project.bucket = row['Bucket']
                project.short_name = row['Short_Name']
                project.long_name = row['Long_Name']
                project.uuid = row['UUID']
                project.keyword_version =row['keyword_version']
                project.keyword_revision_date = row['keyword_revision_date']
                project.download_date = row['download_date']
                project.in_gcmd = settings.DEFAULT_IN_GCMD

                project.save()