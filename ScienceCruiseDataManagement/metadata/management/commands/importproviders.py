from django.core.management.base import BaseCommand, CommandError
from metadata.models import Provider
from django.conf import settings
import csv

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

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
                provider.short_name = row['Short_Name']
                provider.long_name = row['Long_Name']
                provider.data_center_url = row['Data_Center_URL']
                provider.uuid = row['UUID']
                provider.keyword_version =row['keyword_version']
                provider.keyword_revision_date = row['keyword_revision_date']
                provider.download_date = row['download_date']
                provider.in_gcmd = settings.DEFAULT_IN_GCMD

                provider.save()