from django.core.management.base import BaseCommand, CommandError
from metadata.models import HorizontalResolutionRange
from main import utils
from django.conf import settings
import csv
import datetime

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
    help = 'Adds data to the horizontal resolution table'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        self.import_data_from_csv(options['filename'])

    def import_data_from_csv(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                horizontal_resolution_range = HorizontalResolutionRange()
                horizontal_resolution_range.horizontal_resolution_range = row['Horizontal_Resolution_Range']
                horizontal_resolution_range.UUID = row['UUID']
                horizontal_resolution_range.keyword_version = row['keyword_version']
                horizontal_resolution_range.keyword_revision_date = utils.rfc3339_to_datetime(row['keyword_revision_date'])
                horizontal_resolution_range.download_date = utils.rfc3339_to_datetime(row['download_date'])
                horizontal_resolution_range.in_gcmd = settings.DEFAULT_IN_GCMD

                horizontal_resolution_range.save()

