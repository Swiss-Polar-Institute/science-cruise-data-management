from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, Event, Person, Leg
import csv
import datetime
import os


class Command(BaseCommand):
    help = 'People leg 3'

    def add_arguments(self, parser):
        # parser.add_argument('action', type=str)
        pass

    def handle(self, *args, **options):
        self.list()

    def list(self):
        # project = Project.objects.filter(number=16)
        # samples = Sample.objects.filter(project=project).order_by('julian_day')
        people = Person.objects.all()

        print("Saving in {}".format("people-leg3.csv"))
        # f = open("/home/carles/people-leg-3.csv", "w")
        # csv_writer = csv.writer(f)
        # csv_writer.writerow(["event_number", "description", "date_time (UTC)", "latitude", "longitude"])

        leg2 = Leg.objects.get(number=2)
        leg3 = Leg.objects.get(number=3)

        for person in people:
            legs_for_person = person.leg.all()

            if leg2 in legs_for_person and leg3 not in legs_for_person:
                print(str(person))

