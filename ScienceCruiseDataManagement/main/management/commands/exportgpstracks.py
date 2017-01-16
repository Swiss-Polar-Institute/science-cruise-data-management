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
        # print("============ TRIMBLE")
        # find_gps_missings(63)
        # print("============ BRIDGE")
        # find_gps_missings(64)



def generate_all_tracks(output_directory):
    generate_method_2(output_directory, 3600, "1hour")
    generate_method_2(output_directory, 300, "5min")
    generate_method_2(output_directory, 60, "1min")
    generate_method_2(output_directory, 1, "1second")


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
        query_set = GpggaGpsFix.objects.filter(date_time__contains=':00.').order_by('date_time')
    elif seconds == 300:
        query_set = GpggaGpsFix.objects.filter(Q(date_time__contains=':00:00.') |
                                               Q(date_time__contains=':05:00.') |
                                               Q(date_time__contains=':10:00.') |
                                               Q(date_time__contains=':15:00.') |
                                               Q(date_time__contains=':20:00.') |
                                               Q(date_time__contains=':25:00.') |
                                               Q(date_time__contains=':30:00.') |
                                               Q(date_time__contains=':35:00.') |
                                               Q(date_time__contains=':40:00.') |
                                               Q(date_time__contains=':45:00.') |
                                               Q(date_time__contains=':50:00.') |
                                               Q(date_time__contains=':55:00.')).order_by('date_time')
    elif seconds == 3600:
        query_set = GpggaGpsFix.objects.filter(date_time__contains=':00:00').order_by('date_time')
    else:
        assert False # need to add a if case for this

    to_be_written = None
    last_written = None

    # 64: GPS Bridge
    # 63: GPS Trimble

    for gps_info in query_set.iterator():
        date_time_string = gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S")

        if which_gps(date_time_string) == "bridge":
            if gps_info.device_id == 64:
                csv_writer.writerow([gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                     "{:.4f}".format(gps_info.latitude),
                                     "{:.4f}".format(gps_info.longitude)])

        else:
            if gps_info.device_id == 63:
                csv_writer.writerow([gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                     "{:.4f}".format(gps_info.latitude),
                                     "{:.4f}".format(gps_info.longitude)])

        #
        # if which_gps(date_time_string)
        # if to_be_written is not None and date_time_string != to_be_written[0] and date_time_string != last_written:
        #     print("Will write now:", to_be_written[0])
        #     print("Last writing  :", last_written)
        #
        #     csv_writer.writerow(to_be_written)
        #     last_written = to_be_written[0]
        #     print("Written Trimble", to_be_written[0])
        #     to_be_written = None
        #
        #
        # if gps_info.device_id == 64:
        #     csv_writer.writerow([gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
        #                          "{:.4f}".format(gps_info.latitude),
        #                          "{:.4f}".format(gps_info.longitude)])
        #     print("Written Bridge ", gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"))
        #     to_be_written = None
        #     last_written = gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S")
        #
        # else:
        #     to_be_written = [gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
        #                      "{:.4f}".format(gps_info.latitude),
        #                      "{:.4f}".format(gps_info.longitude)]


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


def find_gps_missings(device):
    time_delta = datetime.timedelta(seconds=300)

    first_date = GpggaGpsFix.objects.earliest().date_time
    last_date = GpggaGpsFix.objects.latest().date_time

    current_date = first_date
    previous_state = "disconnected"

    while current_date < last_date:
        location_exists = utils.ship_location_exists(current_date, device)

        if location_exists and previous_state == "disconnected":
            print("Starts at", current_date)
            previous_state = "connected"
        elif not location_exists and previous_state == "connected":
            print("Stops at ", current_date)
            previous_state = "disconnected"

        previous_date = current_date
        current_date = current_date + time_delta

        if previous_date.day != current_date.day:
            print("Processing now {}".format(current_date))

def which_gps(date_time_str):
    gps_bridge_working_intervals = [ ("2016-12-27 13:39:14", "2016-12-28 06:54:14"),
                                     ("2016-12-28 07:09:14", "2017-01-01 10:59:14"),
                                     ("2017-01-01 11:24:14", "2017-01-05 00:04:14"),
                                     ("2017-01-05 02:09:14", "2017-01-11 00:04:14"),
                                     ("2017-01-11 02:34:14", "2017-01-11 08:49:14"),
                                     ("2017-01-11 08:54:14", "2017-01-11 00:04:14"),
                                     ("2017-01-11 02:34:14", "2017-01-11 08:49:14"),
                                     ("2017-01-11 08:54:14", "2017-01-13 08:44:14"),
                                     ("2017-01-13 11:29:14", "2017-12-12 00:00:00")]

    for interval in gps_bridge_working_intervals:
        if date_time_str > interval[0] and date_time_str <= interval[1]:
            return "bridge"

    return "trimble"