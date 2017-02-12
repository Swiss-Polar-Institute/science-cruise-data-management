from django.core.management.base import BaseCommand, CommandError
from metadata.models import DatasetProgress
import csv

class Command(BaseCommand):
    help = 'Adds data to the dataset progress table.'

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
                datasetprogress = DatasetProgress()
                datasetprogress.type = row['Type']
                datasetprogress.definition = row['Definition']
                datasetprogress.download_date= row['download_date']

                datasetprogress.save()