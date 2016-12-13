from django.core.management.base import BaseCommand, CommandError
from main.models import Person
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
                person = Person()
                person.name_first = row['name_first']
                person.name_middle = row['name_middle']
                person.name_last = row['name_last']
                person.save()

