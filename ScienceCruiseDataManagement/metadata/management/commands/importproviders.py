from django.core.management.base import BaseCommand, CommandError
from metadata.models import Provider
import csv

class Command(BaseCommand):
    help = 'Adds data to the provider table.'

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
                provider = Provider()
                provider.bucket_Level0 = row['Bucket_Level0']
                provider.bucket_Level1 = row['Bucket_Level1']
                provider.bucket_Level2 = row['Bucket_Level2']
                provider.bucket_Level3 = row['Bucket_Level3']
                provider.short_name = ['Short_Name']
                provider.long_name = ['Long_Name']
                provider.data_center_url = ['Data_Center_URL']
                provider.uuid = ['UUID']
                provider.keyword_version =row['keyword_version']
                provider.keyword_revision_date = row['keyword_revision_date']
                provider.download_date = row['download_date']

                provider.save()