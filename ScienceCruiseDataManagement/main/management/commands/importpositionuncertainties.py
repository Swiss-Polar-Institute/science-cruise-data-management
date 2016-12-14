from django.core.management.base import BaseCommand, CommandError
from main.models import PositionUncertainty
import csv

class Command(BaseCommand):
    help = 'Adds data to the person table'

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
                positionuncertainty = PositionUncertainty()

                positionuncertainty.table_code = row['table_code']
                positionuncertainty.code = row['code']
                positionuncertainty.name = row['name']
                positionuncertainty.source = row['source']

                positionuncertainty.save()

