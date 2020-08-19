from django.core.management.base import BaseCommand
from main.models import EventAction
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
        next(contents, None) # skip header line
        
        with open(output_filename, 'w') as output_file:
            writer = csv.writer(output_file)

            header = ['event_number', 'start_datetime', 'end_datetime']
            writer.writerow(header)

            for line in contents:
                # read in the event number
                event_number = int(line[0])

                # get the event actions (start and end details) of an event
                event_actions = EventAction.objects.filter(event__pk=event_number)
                print(event_number)
                if len(event_actions) == 1:
                    event_action_datetimes = [event_actions[0].time]  # some events only have an instantaneous time
                else:
                    event_action_datetimes = [event_actions[0].time,
                                              event_actions[1].time]  # some events have a start and end time

                # Convert date time to string format
                event_action_datetimes = list(map(datetime_to_text, event_action_datetimes))

                # Sort list of datetimes so that if there is more than one, the start comes before the end
                event_action_datetimes.sort()

                # Output the event number, and associated date times (there can be more than one datetime so this expands it)
                writer.writerow([event_number, *event_action_datetimes])
