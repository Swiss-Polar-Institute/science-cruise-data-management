from django.core.management.base import BaseCommand, CommandError
from main.models import Project, Person
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
                project = Project()
                project.number = row['project_number']
                project.title= row['project_title']
                project.alternative_title = row['project_alternative_title']
                project.abstract = row['abstract']

                if row['name_first'] != '':
                    print("{}-{}".format(row['name_first'],row['name_last']))
                    person = Person.objects.filter(name_first=row['name_first']).filter(name_last=row['name_last'])[0]
                    project.principal_investigator =person

                project.save()

