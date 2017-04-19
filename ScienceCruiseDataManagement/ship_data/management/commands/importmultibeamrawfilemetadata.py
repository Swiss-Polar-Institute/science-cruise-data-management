from django.core.management.base import BaseCommand, CommandError
from ship_data.models import MultibeamRawFileMetadata
import json
import datetime
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
    help = 'Imports multibeam data'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', help="Base where to find all the *.inf.json files", type=str)

    def handle(self, *args, **options):
        print(options['directory_name'])
        import_multibeam_raw_file_metadata(options['directory_name'])

def iso_to_datetime(text):
    text = text.split(".")[0]

    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")

def import_metadata(base_directory, sub_directory, file_name):
    print(base_directory, sub_directory, file_name)
    file_path = os.path.join(base_directory, sub_directory, file_name)
    fp = open(file_path, "r")
    information = json.load(fp)

    multibeam_raw_file_metadata = MultibeamRawFileMetadata()
    # file_path = models.CharField(max_length=300)
    # directory = models.CharField(max_length=30)
    # swath_data_file = models.CharField(max_length=40)
    # file_start_time_iso = models.DateTimeField()
    # file_end_time_iso = models.DateTimeField()
    # minimum_longitude = models.FloatField()
    # maximum_longitude = models.FloatField()
    # minimum_latitude = models.FloatField()
    # maximum_latitude = models.FloatField()
    # minimum_sonar_depth = models.FloatField()
    # maximum_sonar_depth = models.FloatField()

    multibeam_raw_file_metadata.file_path = base_directory
    multibeam_raw_file_metadata.directory = sub_directory
    multibeam_raw_file_metadata.swath_data_file = file_name.replace("_inf.json", "")
    multibeam_raw_file_metadata.file_start_time = iso_to_datetime(information['start_of_data']['time_iso'])
    multibeam_raw_file_metadata.file_end_time = iso_to_datetime(information['end_of_data']['time_iso'])
    multibeam_raw_file_metadata.minimum_longitude = information['limits']['minimum_longitude']
    multibeam_raw_file_metadata.maximum_longitude = information['limits']['maximum_longitude']
    multibeam_raw_file_metadata.minimum_latitude = information['limits']['minimum_latitude']
    multibeam_raw_file_metadata.maximum_latitude = information['limits']['maximum_latitude']
    multibeam_raw_file_metadata.minimum_sonar_depth = information['limits']['minimum_sonar_depth']
    multibeam_raw_file_metadata.maximum_sonar_depth = information['limits']['maximum_sonar_depth']

    multibeam_raw_file_metadata.save()

    fp.close()


def import_multibeam_raw_file_metadata(directory):
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.endswith("_inf.json"):
                import_metadata(directory, dirpath[len(directory):], filename)