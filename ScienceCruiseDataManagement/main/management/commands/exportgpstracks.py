from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
import datetime
from main import utils
import csv
import os
from django.db.models import Q


class Command(BaseCommand):
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str)

    def handle(self, *args, **options):
        generate_all_tracks(options['output_directory'])


def generate_all_tracks(output_directory):
    # generate_method_1(output_directory, 3600, "1hour")

    # generate_method_2(output_directory, 3600, "1hour")

    generate_method_2(output_directory, 1, "1second")
    generate_method_2(output_directory, 60, "1min")
    generate_method_2(output_directory, 300, "5min")
    generate_method_2(output_directory, 3600, "5min")

def generate_method_2(output_directory, seconds, file_suffix):
    """
    This method uses Mysql datetime 'ends with' instead of doing individual queries
    for each 'seconds'. It's faster but harder to find gaps in the data.
    """
    first_date = GpggaGpsFix.objects.earliest().date_time
    last_date = GpggaGpsFix.objects.latest().date_time

    filename = "track_{}_{}_{}.csv".format(first_date.strftime("%Y%m%d"), last_date.strftime("%Y%m%d"), file_suffix)

    print("Will start processing:", filename)

    file_path = os.path.join(output_directory, filename)

    file = open(file_path, "w")

    csv_writer = csv.writer(file)

    csv_writer.writerow(["date_time", "latitude", "longitude"])

    if seconds == 1:
        query_set = GpggaGpsFix.objects.all().order_by('date_time')
    elif seconds == 60:
        query_set = GpggaGpsFix.objects.filter(date_time__endswith=':00').order_by('date_time')
    elif seconds == 300:
        query_set = GpggaGpsFix.objects.filter(Q(date_time__endswith=':00.00') |
                                               Q(date_time__endswith=':05.00') |
                                               Q(date_time__endswith=':10.00') |
                                               Q(date_time__endswith=':15.00') |
                                               Q(date_time__endswith=':20.00') |
                                               Q(date_time__endswith=':25.00') |
                                               Q(date_time__endswith=':30.00') |
                                               Q(date_time__endswith=':35.00') |
                                               Q(date_time__endswith=':40.00') |
                                               Q(date_time__endswith=':45.00') |
                                               Q(date_time__endswith=':50.00') |
                                               Q(date_time__endswith=':55.00'))
    elif seconds == 3600:
        query_set = GpggaGpsFix.objects.filter(date_time__endswith=':00:00').order_by('date_time')
    else:
        assert False # need to add a if case for this

    for gps_info in query_set.iterator():
        csv_writer.writerow([gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                             "{:.4f}".format(gps_info.latitude),
                             "{:.4f}".format(gps_info.longitude)])


def generate_method_1(output_directory, seconds, file_suffix):
    """
    This method does a query every 'seconds'. Very slow, could be used to find gaps easily on the data.
    """
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
