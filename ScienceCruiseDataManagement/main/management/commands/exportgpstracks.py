from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
import datetime
from main import utils
import csv
import os
from django.db.models import Q
import glob
from main.management.commands import findgpsgaps

gps_bridge_working_intervals = None

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
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str, help="Will delete existing files that started on the same start date")
        parser.add_argument('start', type=str, help="Start of the GPS data. Format: YYYYMMDD")
        parser.add_argument('end', type=str, help="End of the GPS data. Format: YYYYMMDD or 'yesterday'")

    def handle(self, *args, **options):
        generate_all_tracks(options['output_directory'], options['start'], options['end'])


def generate_all_tracks(output_directory, start, end):
    global gps_bridge_working_intervals

    gps_gaps = findgpsgaps.FindDataGapsGps("GPS Bridge1", start, end)

    gps_bridge_working_intervals = gps_gaps.find_gps_missings()

    generate_fast(output_directory, 3600, "1hour", start, end)
    generate_fast(output_directory, 300, "5min", start, end)
    generate_fast(output_directory, 60, "1min", start, end)
    generate_fast(output_directory, 1, "1second", start, end)


def generate_fast(output_directory, seconds, file_suffix, start, end):
    """
    This method uses Mysql datetime 'ends with' instead of doing individual queries
    for each 'seconds'. It's faster but harder to find gaps in the data.
    """
    first_date = datetime.datetime.strptime(start, "%Y%m%d")
    first_date = utils.set_utc(first_date)

    if end == "yesterday":
        last_date = utils.last_midnight()
    else:
        last_date = datetime.datetime.strptime(end, "%Y%m%d")
        last_date = utils.set_utc(last_date)

    starts_file_format = first_date.strftime("%Y%m%d")
    ends_file_format = last_date.strftime("%Y%m%d")

    filename = "track_{}_{}_{}.csv".format(starts_file_format, ends_file_format, file_suffix)

    files_to_delete = glob.glob(os.path.join(output_directory, "track_{}_*_{}.csv".format(starts_file_format,
                                                                                          file_suffix)))
    print("Will start processing:", filename)

    file_path = os.path.join(output_directory, filename)

    if file_path in files_to_delete:
        files_to_delete.remove(file_path)   # In case that this script is re-generating the file

    file = open(file_path + ".tmp", "w")

    csv_writer = csv.writer(file)

    csv_writer.writerow(["date_time", "latitude", "longitude"])

    one_day = datetime.timedelta(days=1)

    current_day = first_date
    while current_day <= last_date:
        process_day(current_day, seconds, csv_writer)
        current_day += one_day

    delete_files(files_to_delete)

    file.close()

    os.rename(file_path + ".tmp", file_path)


def process_day(date_time_process, seconds, csv_writer):
    date_time_process_tomorrow = date_time_process + datetime.timedelta(days=1)

    today_filter = Q(date_time__gte=date_time_process) & Q(date_time__lt=date_time_process_tomorrow)
    if seconds == 1:
        query_set = GpggaGpsFix.objects.filter(today_filter).order_by('date_time')
    elif seconds == 60:
        query_set = GpggaGpsFix.objects.filter(today_filter).filter(date_time__contains=':01.').order_by('date_time')
    elif seconds == 300:
        query_set = GpggaGpsFix.objects.filter(today_filter).filter(Q(date_time__contains=':00:01.') |
                                               Q(date_time__contains=':05:01.') |
                                               Q(date_time__contains=':10:01.') |
                                               Q(date_time__contains=':15:01.') |
                                               Q(date_time__contains=':20:01.') |
                                               Q(date_time__contains=':25:01.') |
                                               Q(date_time__contains=':30:01.') |
                                               Q(date_time__contains=':35:01.') |
                                               Q(date_time__contains=':40:01.') |
                                               Q(date_time__contains=':45:01.') |
                                               Q(date_time__contains=':50:01.') |
                                               Q(date_time__contains=':55:01.')).order_by('date_time')
    elif seconds == 3600:
        query_set = GpggaGpsFix.objects.filter(today_filter).filter(date_time__contains=':00:01').order_by('date_time')
    else:
        assert False # need to add a if case for this

    # 64: GPS Bridge
    # 63: GPS Trimble

    query_set = query_set.filter(utils.filter_out_bad_values())

    previous_date_time_string = ""
    for gps_info in query_set.iterator():
        date_time_string = gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S")

        if date_time_string == previous_date_time_string:
            continue

        if which_gps(date_time_string) == "GPS Bridge1":
            if gps_info.device_id == 64:
                l = [gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                     "{:.4f}".format(gps_info.latitude),
                                     "{:.4f}".format(gps_info.longitude)]
                # print(l)
                csv_writer.writerow(l)
                previous_date_time_string = date_time_string

        else:
            if gps_info.device_id == 63:
                l = [gps_info.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                     "{:.4f}".format(gps_info.latitude),
                                     "{:.4f}".format(gps_info.longitude)]
                # print(l)
                csv_writer.writerow(l)

                previous_date_time_string = date_time_string

def delete_files(files):
    for file in files:
        print("Deleting file:", file)
        os.remove(file)


def generate_method_1(output_directory, seconds, file_suffix):
    """
    This method does a query every 'seconds'. Very slow, could be used to find gaps easily on the data.
    As it is now it is difficult to decide which GPS the get comes from.
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
            print("Generating CSV GPS info:", current_date)

        previous_date = current_date
        current_date = current_date + time_delta


def which_gps(date_time_str):
    for interval in gps_bridge_working_intervals:
        if interval['starts'] < date_time_str <= interval['stops']:
        # if date_time_str > interval['starts'] and date_time_str <= interval['stops']:
            return "GPS Bridge1"

    return "Trimble GPS"
