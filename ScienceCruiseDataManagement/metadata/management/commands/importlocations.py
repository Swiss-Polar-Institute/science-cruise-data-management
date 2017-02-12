from django.core.management.base import BaseCommand, CommandError
from metadata.models import Location
import csv

class Command(BaseCommand):
    help = 'Adds data to the location table.'
















class Command(BaseCommand):
    help = 'Adds data to the mission table'

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
                mission = Mission()
                mission.name = row['name']
                mission.acronym= row['acronym']
                mission.institution = row['institution']
                mission.description = row['description']

                mission.save()