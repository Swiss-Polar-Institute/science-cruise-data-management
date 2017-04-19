from django.core.management.base import BaseCommand, CommandError
from main.models import Person, Organisation
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


                person.initials = self.create_initials(person)



                if row['organisation'] != '':
                    list_of_organisations = row['organisation'].split(";")

                    for organisation_listed in list_of_organisations:
                        organisation_listed = organisation_listed.strip()
                        print(organisation_listed)
                        organisation = Organisation.objects.filter(name=organisation_listed)[0]
                        person.save()
                        person.organisation.add(organisation)

                person.save()

    @staticmethod
    def initials_from_person(person, surname_letters):
        return "{}{}".format(person.name_first[0], person.name_last[0:surname_letters])

    @staticmethod
    def create_initials(person):
        letters = 1
        initials = Command.initials_from_person(person, letters)
        while Person.objects.filter(initials=initials).exists():
            letters += 1
            initials = Command.initials_from_person(person, letters)

        return initials

