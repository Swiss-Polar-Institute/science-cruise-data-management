from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, Event
from django.conf import settings

from main import utils
import csv

class Command(BaseCommand):
    help = 'Get dates and times of an event'

    def add_arguments(self, parser):
        parser.add_argument('input_filename', help="Filename containing the event numbers", type=str)
        parser.add_argument('output_filename', help="Filename to output the data into", type=str)

    def handle(self, *args, **options):
        process_input_file(options['input_filename'], options['output_filename'])

def datetime_to_text(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def process_input_file(input_filename, output_filename):

    with open(input_filename, 'r') as data_file:
        contents = csv.reader(data_file)

        for line in contents:
            #print("Line: ", line)
            event_number = int(line[0])
            #print("Event number: ", event_number)

            #event = Event.objects.get(id=event_number)
            event_actions = EventAction.objects.filter(event__pk=event_number)
            if len(event_actions) == 1:
                event_action_datetimes = [datetime_to_text(event_actions[0].time)]
            else:
                event_action_datetimes = [datetime_to_text(event_actions[0].time), datetime_to_text(event_actions[1].time)]

            event_action_datetimes.sort()

            print(",".join(event_action_datetimes))


