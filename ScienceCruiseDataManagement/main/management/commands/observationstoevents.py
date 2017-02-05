from django.core.management.base import BaseCommand, CommandError
import csv
import datetime
import os


class Command(BaseCommand):
    help = 'Converts an observations spreadsheet to events one (so then it can be imported)'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.convert_spreadsheet(options['filename'])

    def convert_spreadsheet(self, input_filename):
        csv_reader = csv.reader(open(input_filename, encoding = 'utf-8', errors='ignore'))

        new_filename = os.path.basename(input_filename)

        new_path = os.path.dirname(input_filename)
        new_filename = "Events-" + new_filename

        new_filepath = os.path.join(new_path, new_filename)

        csv_writer = csv.writer(open(new_filepath, "w"))

        csv_writer.writerow(['parent_device', 'data', 'samples', 'start_time', 'type', 'what_happened_start', 'end_time', 'type', 'what_happened_end', 'time_source', 'time_uncertainty', 'general_comments'])

        input_spreadsheet = []
        for line in csv_reader:
            input_spreadsheet.append(line)

        column = column_after_headers(input_spreadsheet)

        current_event_start_date_time_formatted = None
        last_stop_time_formatted = None
        last_start_time_formatted = None
        last_stop_time_formatted = None

        while column < number_of_columns(input_spreadsheet):
            current_start_time = input_spreadsheet[gmt_start_row()][column]
            current_stop_time = input_spreadsheet[gmt_stop_row()][column]
            current_date = input_spreadsheet[date_row()][column]

            if current_date == "":
                break

            if "Dec" in current_date:
                year = 2016
            else:
                year = 2017

            formatted_current_start_date_time = datetime.datetime.strptime("{}-{} {}".format(current_date, year, current_start_time), "%d-%b-%Y %H:%M")
            formatted_current_stop_date_time = datetime.datetime.strptime("{}-{} {}".format(current_date, year, current_stop_time), "%d-%b-%Y %H:%M")

            if current_event_start_date_time_formatted is None:
                current_event_start_date_time_formatted = formatted_current_start_date_time

            if last_start_time_formatted is not None and last_stop_time_formatted is not None \
                    and ((formatted_current_start_date_time != last_stop_time_formatted or
                              (column + 1 == number_of_columns(input_spreadsheet)))): # it's the last one

                if column + 1 == number_of_columns(input_spreadsheet):
                    last_stop_time_formatted = formatted_current_stop_date_time

                print("Create new event:", current_event_start_date_time_formatted, last_stop_time_formatted)
                csv_writer.writerow(['Predator observing', 'True', 'False', current_event_start_date_time_formatted, 'Begins', 'started',
                                    last_stop_time_formatted, 'ends', 'stopped', 'personal watch', 'minutes', ''])

                current_event_start_date_time_formatted = formatted_current_start_date_time

            last_start_time_formatted = formatted_current_start_date_time
            last_stop_time_formatted = formatted_current_stop_date_time

            column += 1

        print("Spreadsheet as event format as", new_filepath)


def number_of_columns(spreadsheet):
    return len(spreadsheet[0])


def column_after_headers(spreadsheet):
    """ Returns the column number for 21-Dec (start of the expedition). """
    for (i, cell) in enumerate(spreadsheet[date_row()]):
        if cell == "21-Dec":
            return i

    # Column not found with 21-Dec
    assert False

def gmt_start_row():
    return 4


def gmt_stop_row():
    return 5


def date_row():
    return 0
