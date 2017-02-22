from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, Event
import csv
import datetime
import os


class Command(BaseCommand):
    help = 'List of samples for Chileans'

    def add_arguments(self, parser):
        # parser.add_argument('action', type=str)
        pass

    def handle(self, *args, **options):
        self.list()

    def list(self):
        # project = Project.objects.filter(number=16)
        # samples = Sample.objects.filter(project=project).order_by('julian_day')
        event_actions = EventAction.objects.filter(latitude__gte=-68.6).filter(time__gte="2017-02-15").order_by('time')

        print("Saving in {}".format("chilean-border.csv"))
        f = open("/home/data/chilean-border", "w")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["event_number", "date_time (UTC)", "latitude", "longitude"])

        for event_action in event_actions:
            event_number = event_action.event.number
            sampling_method = event_action.event.sampling_method
            date_time = event_action.time
            latitude = event_action.latitude
            longitude = event_action.longitude

            csv_writer.writerow([event_number, sampling_method, date_time, latitude, longitude])

        f.close()
