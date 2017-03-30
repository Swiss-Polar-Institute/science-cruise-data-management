from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Project, EventAction, SamplingMethod, SpecificDevice
from data_storage_management.models import Directory
import csv
from django.core.exceptions import ObjectDoesNotExist
import json
import os


class Command(BaseCommand):
    help = 'Converts the data coverage JSON file (specifying the start/end) into events sheet'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            type=str,
                            help='JSON file with a list of starts/stops')
        parser.add_argument('parent_device',
                            type=str,
                            help="Parent device name")

    def handle(self, *args, **options):
        file_path = options['file']
        parent_device = options['parent_device']

        convert(file_path, parent_device)

def create_event(starts, ends, parent_device):
    event = {}

    event['parent_device'] = parent_device
    event['data'] = "True"
    event['samples'] = "False"
    event['start_time'] = starts
    event['type'] = "Begins"
    event['what_happened_start'] = "started"
    event['end_time'] = ends
    event['type'] = "ends"
    event['what_happened_end'] = "stopped"
    event['time_source'] = "Ship's GPS"
    event['time_uncertainty'] = "Seconds"
    event['general_comments'] = ""

    return event

def convert(file_path, parent_device):
    basename = os.path.basename(file_path)
    basename = os.path.splitext(basename)[0]

    event_file_name = "Events-{}.csv".format(basename)

    json_file = open(file_path, "r")
    event_file = open(event_file_name, "w")
    event_sheet = csv.DictWriter(event_file, ['parent_device', 'data', 'samples', 'start_time', 'type',
                                              'what_happened_start', 'end_time', 'type', 'what_happened_end',
                                              'time_source', 'time_uncertainty', 'general_comments'])

    d = json.load(json_file)
    event_sheet.writeheader()

    for data_coverage in d:
        event = create_event(data_coverage['starts'], data_coverage['stops'], parent_device)

        print(event)
        event_sheet.writerow(event)
