from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
import datetime
from main import utils
import csv
import os


class Command(BaseCommand):
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str)

    def handle(self, *args, **options):
        generate_all_tracks(options['output_directory'])


def generate_all_tracks(output_directory):
    generate(output_directory, 1, "1second")
    generate(output_directory, 60, "1min")
    generate(output_directory, 300, "5min")
    generate(output_directory, 3600, "1hour")


def generate(output_directory, seconds, file_suffix):
    time_delta = datetime.timedelta(seconds=seconds)

    first_date = GpggaGpsFix.objects.earliest().date_time
    last_date = GpggaGpsFix.objects.latest().date_time

    filename = "track_{}_{}_{}.csv".format(first_date.strftime("%Y%m%d"), last_date.strftime("%Y%m%d"), file_suffix)

    print("Will start processing:", filename)

    file_path = os.path.join(output_directory, filename)

    file = open(file_path, "w")

    csv_writer = csv.writer(file)

    csv_writer.writerow(["date_time", "latitude", "longitude"])

    current_date = first_date
    previous_date = current_date

    while current_date < last_date:
        location = utils.ship_location(current_date)

        if location.date_time != previous_date:
            if location.date_time is not None and location.latitude is not None and location.longitude is not None:
                csv_writer.writerow([location.date_time.strftime("%Y-%m-%d %H:%M:%S"), "{:.4f}".format(location.latitude), "{:.4f}".format(location.longitude)])

        if location.date_time is None:
            print("No data for:", current_date)

        if previous_date.day != current_date.day:
            print("Processing now:", current_date)

        previous_date = current_date
        current_date = current_date + time_delta
