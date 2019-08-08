from django.core.management.base import BaseCommand, CommandError
from ship_data.models import CruiseTrack
from main.models import SamplingMethod
import csv
from main import utils
from ship_data import utilities
import datetime
import glob
import os

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
    help = 'Adds data to the cruise track table'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', type=str, help="Directory from where the .csv files will be imported.")

    def handle(self, *args, **options):
        cruisetrack_filepath = options["directory_name"]
        self.import_data_from_csv(cruisetrack_filepath)

    def import_data_from_csv(self, cruisetrack_filepath):
        files = glob.glob(os.path.join(cruisetrack_filepath, "*.csv"))
        files.sort()

        for filename in files:

            with open(filename) as csvfile:
                reader = csv.DictReader(csvfile)
                counter = 0

                for row in reader:

                    if counter%1000 == 0:
                        print(row)

                    device = SamplingMethod.objects.get(id=int(row['device_id']))

                    cruise_track = CruiseTrack()
                    cruise_track.date_time = utils.set_utc(datetime.datetime.strptime(row['date_time'], '%Y-%m-%dT%H:%M:%S.%f+00:00'))
                    cruise_track.latitude = float(row['latitude'])
                    cruise_track.longitude = float(row['longitude'])
                    cruise_track.fix_quality = int(row['fix_quality'])
                    cruise_track.number_satellites = int(row['number_satellites'])
                    cruise_track.horiz_dilution_of_position = float(row['horiz_dilution_of_position'])
                    cruise_track.altitude = float(row['altitude'])
                    cruise_track.altitude_units = row['altitude_units']
                    cruise_track.geoid_height = float(row['geoid_height'])
                    cruise_track.geoid_height_units = row['geoid_height_units']
                    cruise_track.device = device
                    cruise_track.speed = float(row['speed'])
                    cruise_track.measureland_qualifier_flag_overall = int(row['measureland_qualifier_flag_overall'])

                    cruise_track.save()
                    counter += 1

            print("File complete: ", filename)