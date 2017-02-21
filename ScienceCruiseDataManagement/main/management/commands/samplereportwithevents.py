from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Project
import csv
import datetime
import os


class Command(BaseCommand):
    help = 'List samples with the events, positions and times'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)

    def handle(self, *args, **options):
        self.list()

    def list(self):
        project = Project.objects.filter(number=16)
        samples = Sample.objects.filter(project=project).order_by('julian_day')

        print("Saving in {}".format("samplereportevent.csv"))
        f = open("samplereportevent.csv", "w")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["sample_number", "project_sample_number", "event", "station", "latitude", "longitude", "time (UTC)"])

        for sample in samples:
            sample_number = sample.expedition_sample_code
            project_sample_number = sample.project_sample_number
            event_number = sample.event_id

            if sample.event is not None and sample.event.station is not None:
                station_number = sample.event.station.name
                latitude = sample.event.station.latitude
                longitude = sample.event.station.longitude
                date_time = sample.event.station.arrival_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                latitude = longitude = date_time = station_number = ""

            csv_writer.writerow([sample_number, project_sample_number, event_number, station_number, latitude, longitude, date_time])

        f.close()
