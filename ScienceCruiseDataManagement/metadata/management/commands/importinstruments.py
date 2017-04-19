from django.core.management.base import BaseCommand, CommandError
from metadata.models import Instrument
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
    help = 'Adds data to the instrument table.'

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
                instrument = Instrument()
                instrument.category = row['Category']
                instrument.instrument_class = row['Class']
                instrument.type = row['Type']
                instrument.subtype = row['Subtype']
                instrument.short_name = row['Short_Name']
                instrument.long_name = row['Long_Name']
                instrument.uuid = row['UUID']
                instrument.keyword_version = row['keyword_version']
                instrument.keyword_revision_date = row['keyword_revision_date']
                instrument.download_date = row['download_date']
                instrument.in_gcmd = settings.DEFAULT_IN_GCMD

                instrument.save()