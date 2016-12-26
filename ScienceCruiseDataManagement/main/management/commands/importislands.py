from django.core.management.base import BaseCommand, CommandError
from main.models import Island
import csv

class Command(BaseCommand):
    help = 'Adds data to the island table'

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
                island = Island()
                island.name = row['name']

                if row['mid_lat'] != '':
                    island.mid_lat = float(row['mid_lat'])

                if row['mid_lon'] != '':
                    island.mid_lon = float(row['mid_lon'])

                island.save()

