from django.core.management.base import BaseCommand, CommandError
from main.models import Person, Organisation
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
                person.initials = self.initials_from_person(person)

                if row['organisation'] != '':
                    list_of_organisations = row['organisation'].split(";")

                    for organisation_listed in list_of_organisations:
                        organisation_listed = organisation_listed.strip()
                        print(organisation_listed)
                        organisation = Organisation.objects.all().filter(name=organisation_listed)[0]
                        person.save()
                        person.organisation.add(organisation)

                person.save()

    @staticmethod
    def initials_from_person(person):
        return "{}{}".format(person.name_first[0], person.name_last[0])