from django.core.management.base import BaseCommand, CommandError
from metadata.models import Parameter
import csv

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

                parameter.save()