from django.core.management.base import BaseCommand, CommandError
from main.models import SamplingMethod
from django.db.models import Q
import datetime
from main import utils
import json
import os
import shutil
import glob

from ship_data.models import GpggaGpsFix


class Command(BaseCommand):
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('gps', type=str, help="Gps device name (SamplingMethod) to find the gaps (e.g. 'GPS Bridge1' or 'GPS Trimble'")
        parser.add_argument('output_directory', type=str, help="Output directory with the JSON data")
        parser.add_argument('basefilename', type=str, help="e.g. gaps-bridge1 . Start, end date and .json will be appended")
        parser.add_argument('start', type=str, help="Start of the GPS data. Format: YYYYMMDD")
        parser.add_argument('end', type=str, help="End of the GPS data. Format: YYYYMMDD or 'yesterday'")

    def handle(self, *args, **options):
        find_data_gaps_gps = FindDataGapsGps(options['gps'], options['start'], options['end'])
        find_data_gaps_gps.save(options['output_directory'], options['basefilename'])


class FindDataGapsGps:
    def __init__(self, device_str, wanted_start_str, wanted_end_str):
        # Find device id
        device = SamplingMethod.objects.get(name=device_str)
        self.device_id = device.id

        # Find first_date
        first_date = datetime.datetime.strptime(wanted_start_str, "%Y%m%d")
        first_date_database_qs = GpggaGpsFix.objects.filter(device_id=self.device_id).filter(Q(date_time__gte=first_date)).order_by('date_time')
        first_date_database = first_date_database_qs.first().date_time

        first_date = utils.set_utc(first_date)
        first_date_database = utils.set_utc(first_date_database)

        if first_date < first_date_database:
            first_date = first_date_database

        self.first_date = first_date
        self.first_date_str = first_date.strftime("%Y-%m-%d %H:%M:%S")

        # Find last_date
        if wanted_end_str == "yesterday":
            last_date = utils.last_midnight()
        else:
            last_date = utils.set_utc(datetime.datetime.strptime(wanted_end_str, "%Y%m%d"))

        self.last_date = last_date
        self.last_date_str = last_date.strftime("%Y-%m-%d %H:%M:%S")

    def save(self, output_directory, basefilename):
        first_only_date = self.first_date.strftime("%Y%m%d")
        last_only_date = self.last_date.strftime("%Y%m%d")
        filename = "{}-{}-{}.json".format(basefilename, first_only_date, last_only_date)

        files_to_delete = glob.glob(os.path.join(output_directory, "{}-{}-*.json".format(basefilename, first_only_date)))

        filename_tmp = "{}.tmp".format(filename)
        file_path = os.path.join(output_directory, filename)
        file_path_tmp = os.path.join(output_directory, filename_tmp)

        fp = open(file_path_tmp, "w")

        gps_missings = self.find_gps_missings()

        json.dump(gps_missings, fp, indent=2, sort_keys=True)

        fp.close()
        shutil.move(file_path_tmp, file_path)
        print("Will delete these files")
        print(files_to_delete)

        for file_to_delete in files_to_delete:
            os.remove(file_to_delete)

        print("Output results with the gps saved in: {}".format(file_path))

    def find_gps_missings(self):
        """ Used to find missing gaps in the GPS information. """
        time_delta = datetime.timedelta(seconds=30)

        current_date = self.first_date
        previous_state = None

        gps_information = []
        while current_date <= self.last_date:
            location_exists = utils.ship_location_exists(current_date, self.device_id)

            if previous_state is None:
                period = {}
                if location_exists:
                    previous_state = "connected"
                    period['starts'] = current_date.strftime("%Y-%m-%d %H:%M:%S")

                else:
                    # The first time per definition should be connected
                    assert False

            if location_exists and previous_state == "disconnected":
                period = {}
                period['starts'] = current_date.strftime("%Y-%m-%d %H:%M:%S")
                print("Starts at", current_date)
                previous_state = "connected"
            elif not location_exists and previous_state == "connected":
                period['stops'] = current_date.strftime("%Y-%m-%d %H:%M:%S")
                print("Stops at ", current_date)
                previous_state = "disconnected"

                gps_information.append(period)

            previous_date = current_date

            if previous_date.day != current_date.day:
                print("Processing {}".format(current_date))

            current_date = current_date + time_delta

            if previous_date.day != current_date.day:
                print("Finding gaps on: {}".format(current_date))

        if 'starts' in period:
            period['stops'] = current_date.strftime("%Y-%m-%d %H:%M:%S")
            gps_information.append(period)

        return gps_information
