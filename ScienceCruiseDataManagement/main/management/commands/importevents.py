from django.core.management.base import BaseCommand, CommandError
from main.models import Event, EventAction, SamplingMethod, TimeSource, TimeUncertainty,\
    PositionSource, PositionUncertainty, EventActionDescription, ImportedFile
from main import utils

import csv
import glob
import codecs
from django.db import transaction
import os


class Command(BaseCommand):
    help = 'Adds data to the events table'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', type=str)

    def handle(self, *args, **options):
        # print(options['directory_name'])
        self.import_data_from_directory(options['directory_name'])

    def import_data_from_directory(self, directory_name):
        for file in glob.glob(directory_name + "/*.csv"):
            self.process_filename(file)

    def convert_to_boolean(self, value):
        if value == "True":
            return True
        elif value == "False":
            return False
        else:
            # The boolean wasn't True neither False?
            assert False


    def find_foreign_key_object(self, possible_column_names, row, model, field, missing_ok=False):
        column_name = None

        for possible_column_name in possible_column_names:
            if possible_column_name in row:
                column_name = possible_column_name

        if column_name is None and missing_ok==True:
            return None

        if column_name is None:
            print("Wanted to find a column name like one of:",possible_column_names,"but not found. Aborting")
            exit(1)

        value = row[column_name]

        while True:
            query_set = model.objects.filter(**{field: value})
            if len(query_set) == 0:
                print("Processing row: ", row)
                print("Wanted a '{}' with field: '{}' and value: '{}' but not found".format(model, field, value))
                print("Please change the database to have it and press ENTER. Or cancel the import of this spreadsheet (Ctl+C)")
                input()
            elif len(query_set) > 1:
                print("Processing row: ", row)
                print("Wanted a '{}' with field '{}' and value: '{}' but found more than one".format(model, field, value))
                print("Please change the database to have only one and press ENTER. Or cancel the import of this spreadsheet (Ctl+C)")
            else:
                return query_set[0]

    def process_filename(self, filepath):
        with codecs.open(filepath, encoding = 'utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)

            events_to_be_inserted = []

            # It will ask for confirmation if there is an event with the same
            # fields as the event that is going to be inserted
            ask_confirmation = False

            for row in reader:
                # Save event
                data = self.convert_to_boolean(row['data'])
                samples = self.convert_to_boolean(row['samples'])

                event = Event()
                event.data = data
                event.samples = samples
                event.sampling_method = self.find_foreign_key_object(['sampling_method', 'parent_device'],
                                                                     row,
                                                                     SamplingMethod,
                                                                     'name')
                event.outcome = "Success"
                event.comments= row['general_comments']

                time_uncertainty = self.find_foreign_key_object(['time_uncertainty'],
                                                                row,
                                                                TimeUncertainty,
                                                                'name')
                time_source = self.find_foreign_key_object(['time_source'],
                                                           row,
                                                           TimeSource,
                                                           'name')

                description_begin = self.find_foreign_key_object(['what_happened_start'],
                                                           row,
                                                           EventActionDescription,
                                                           'name')

                description_end = self.find_foreign_key_object(['what_happened_end'],
                                                               row,
                                                               EventActionDescription,
                                                               'name')

                position_source = self.find_foreign_key_object(['position_source'],
                                                               row,
                                                               PositionSource,
                                                               'name', missing_ok=True)
                position_uncertainty = self.find_foreign_key_object(['position_uncertainty'],
                                                                    row,
                                                                    PositionUncertainty,
                                                                    'name', mission_ok=True)

                # Save event action begin
                event_action_begin = EventAction()
                event_action_begin.time = utils.string_to_date_time(row['start_time'])

                if event_action_begin.time is None:
                    print("Row", row)

                event_action_begin.description = description_begin
                event_action_begin.type = EventAction.tbegin()
                event_action_begin.time_source = time_source
                event_action_begin.time_uncertainty = time_uncertainty
                event_action_begin.latitude = row.get('start_latitude', None)
                event_action_begin.longitude = row.get('start_longitude', None)
                event_action_begin.position_source = position_source
                event_action_begin.position_uncertainty = position_uncertainty

                # Save event action end
                event_action_end = EventAction()
                event_action_end.time = utils.string_to_date_time(row['end_time'])
                event_action_end.description = description_end
                event_action_end.type = EventAction.tends()
                event_action_end.latitude = row.get('end_latitude', None)
                event_action_end.longitude = row.get('end_longitude', None)

                if event_action_begin.time is None:
                    print("Row", row)

                event_action_end.time_source = time_source
                event_action_end.time_uncertainty = time_uncertainty
                event_action_end.position_source = position_source
                event_action_end.position_uncertainty = position_uncertainty

                ask_confirmation |= self.report_event_exists(event)
                ask_confirmation |= self.report_event_action_exists(event_action_begin)
                ask_confirmation |= self.report_event_action_exists(event_action_end)

                events_to_be_inserted.append((event, event_action_begin, event_action_end))

        if ask_confirmation:
            print("Some rows already existed, do you want to import all the spreadsheet? (yes/no)")
            answer = input()

            if answer != "yes":
                print("Aborting")
                exit(1)

        # insert_objects actually always return True (or it throws an exception)
        success = self.insert_objects(events_to_be_inserted)
        if success:
            #
            utils.add_imported(filepath, "Events")

    def event2str(self, event):
        event_str = """EVENT
number: {number}
sampling_method: {sampling_method}
station: {station}
data: {data}
samples: {samples}
outcome: {outcome}
""".format(**{'number': event.number,
              'sampling_method': event.sampling_method,
              'station': event.station,
              'data': event.data,
              'samples': event.samples,
              'outcome': event.outcome})

        return event_str

    def event_action2str(self, event_action):

        event_action_str = """EVENT ACTION
id: {id}
type: {type}
time: {time}
time_source: {time_source}
time_uncertainty: {time_uncertainty}
latitude: {latitude}
longitude: {longitude}
position_source: {position_source}
position_uncertainty: {position_uncertainty}
water_depth: {water_depth}
general_comments: {general_comments}
data_source_comments: {data_source_comments}
""".format(**{'id': event_action.id,
              'type': event_action.type,
              'time': event_action.time,
              'time_source': event_action.time_source,
              'time_uncertainty': event_action.time_uncertainty,
              'latitude': event_action.latitude,
              'longitude': event_action.longitude,
              'position_source': event_action.position_source,
              'position_uncertainty': event_action.position_uncertainty,
              'water_depth': event_action.water_depth,
              'general_comments': event_action.general_comments,
              'data_source_comments': event_action.data_source_comments})

        return event_action_str

    def report_event_exists(self, event):
        query_filter = Event.objects.filter(sampling_method=event.sampling_method).filter(data=event.data).filter(samples=event.samples).filter(outcome=event.outcome)

        if len(query_filter) > 0:
            print("There are some rows in the database very similar to the existing ones:")
            print("Event in the file:", self.event2str(event))
            for event_db in query_filter:
                print("Event in the database:", self.event2str(event_db))

        return query_filter.exists()

    def report_event_action_exists(self, event_action):
        query_filter = EventAction.objects.filter(time=event_action.time).filter(type=event_action.type).filter(time_source=event_action.time_source).filter(time_uncertainty=event_action.time_uncertainty)

        if len(query_filter) > 0:
            print("There are some rows in the database very similar to the existing ones:")
            print("EventAction in the file:", self.event_action2str(event_action))
            for event_db in query_filter:
                print("EventAction in the database:", self.event_action2str(event_db))

        return query_filter.exists()

    @transaction.atomic
    def insert_objects(self, events):
        for complete_event in events:
            event = complete_event[0]
            event_action_begins = complete_event[1]
            event_action_ends = complete_event[2]

            event.save()
            event_action_begins.event = event
            event_action_ends.event = event

            event_action_begins.save()
            event_action_ends.save()

        return True