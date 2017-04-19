from django.core.management.base import BaseCommand, CommandError
from metadata.models import Parameter
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
    help = 'Adds data to the parameter table. Note that the file being imported is science keywords.'

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
                parameter = Parameter()
                parameter.category = row['Category']
                parameter.topic = row['Topic']
                parameter.term = row['Term']
                parameter.variable_level_1 = row['Variable_Level_1']
                parameter.variable_level_2 = row['Variable_Level_2']
                parameter.variable_level_3 = row['Variable_Level_3']
                parameter.detailed_variable = row['Detailed_Variable']
                parameter.uuid = row['UUID']
                parameter.keyword_version = row['keyword_version']
                parameter.keyword_revision_date = row['keyword_revision_date']
                parameter.download_date= row['download_date']
                parameter.in_gcmd = settings.DEFAULT_IN_GCMD

                parameter.save()