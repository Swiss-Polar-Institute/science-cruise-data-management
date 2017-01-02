from django.core.management.base import BaseCommand, CommandError
from main.models import Ship, Platform
import csv

class Command(BaseCommand):
    help = 'Adds data to the ship table'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'])

    def import_data_from_csv(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ship = Ship()

                if row['name'] != '':
                    platform = Platform.objects.filter(name=row['name'])[0]
                    ship.name = platform
                else:
                    print(row)

                ship.imo = row['imo']
                ship.callsign = row['callsign']
                ship.length = row['length']
                ship.breadth = row['breadth']
                ship.power = row['power']
                ship.gross_weight = row['gross_weight']
                ship.noise_design = row['noise_design']
                ship.noise = row['noise']
                ship.notes = row['notes']
                print(row['source'])
                ship.source = row['source']

                ship.save()

