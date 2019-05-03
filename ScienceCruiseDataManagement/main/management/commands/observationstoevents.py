from django.core.management.base import BaseCommand, CommandError
import csv
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

def string2datetime(string):
    try:
        date_time = datetime.datetime.strptime(string, "%d-%b-%Y %H:%M")
    except ValueError:
        string = string.replace("Dez", "Dec")
        string = string.replace("Mrz", "Mar")
        date_time = datetime.datetime.strptime(string, "%d. %b-%Y %H:%M")

    return date_time

class Command(BaseCommand):
    help = 'Converts an observations spreadsheet to events one (so then it can be imported)'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.convert_spreadsheet(options['filename'])

    def convert_spreadsheet(self, input_filename):
        csv_reader = csv.reader(open(input_filename, encoding='utf-8', errors='ignore'))

        new_filename = os.path.basename(input_filename)

        new_path = os.path.dirname(input_filename)
        new_filename = "Events-" + new_filename

        new_filepath = os.path.join(new_path, new_filename)

        csv_writer = csv.writer(open(new_filepath, "w"))

        csv_writer.writerow(['parent_device', 'data', 'samples', 'start_date_time', 'type', 'what_happened_start', 'end_date_time', 'type', 'what_happened_end', 'time_source', 'time_uncertainty', 'general_comments'])

        input_spreadsheet = []
        for line in csv_reader:
            input_spreadsheet.append(line)

        column = column_after_headers(input_spreadsheet)

        current_event_start_date_time_formatted = None
        current_start_date = None
        previous_start_time_formatted = None
        previous_stop_time_formatted = None

        while column < number_of_columns(input_spreadsheet):
            current_start_date = input_spreadsheet[gmt_date_row()][column]
            current_start_time = input_spreadsheet[gmt_start_time_row()][column]
            current_stop_time = input_spreadsheet[gmt_stop_time_row()][column]
            current_date = input_spreadsheet[gmt_date_row()][column]

            if current_date == "":
                break

            if "Dec" in current_date or "Dez" in current_date:
                year = 2016
            else:
                year = 2017

            formatted_current_start_date_time = string2datetime("{}-{} {}".format(current_date, year, current_start_time))
            formatted_current_stop_date_time = string2datetime("{}-{} {}".format(current_date, year, current_stop_time))

            if formatted_current_stop_date_time.hour == 0 and formatted_current_stop_date_time.minute == 0:
                # In the spreadsheet this actually means the day after 00:00, else it would go back in time
                formatted_current_stop_date_time += datetime.timedelta(days=1)

            if current_event_start_date_time_formatted is None:
                current_event_start_date_time_formatted = formatted_current_start_date_time

            if previous_start_time_formatted is not None and previous_stop_time_formatted is not None \
                    and ((formatted_current_start_date_time != previous_stop_time_formatted or
                              (column + 1 == number_of_columns(input_spreadsheet)))): # it's the last one

                if column + 1 == number_of_columns(input_spreadsheet):
                    previous_stop_time_formatted = formatted_current_stop_date_time

                print("Create new event:", current_event_start_date_time_formatted, previous_stop_time_formatted)
                csv_writer.writerow(['Predator observing', 'True', 'False', current_event_start_date_time_formatted, 'Begins', 'started',
                                    previous_stop_time_formatted, 'ends', 'stopped', 'personal watch', 'minutes', ''])

                current_event_start_date_time_formatted = formatted_current_start_date_time

            previous_start_time_formatted = formatted_current_start_date_time
            previous_stop_time_formatted = formatted_current_stop_date_time

            column += 1

        print("Spreadsheet as event format as", new_filepath)


def number_of_columns(spreadsheet):
    return len(spreadsheet[0])


def column_after_headers(spreadsheet):
    """ Returns the column number for 21-Dec (start of the expedition). """
    for (i, cell) in enumerate(spreadsheet[gmt_date_row()]):
        print("_"+cell+"_")
        if cell == "06-Mar": # it used to be 21-Dec but now we import a partial spreadsheet
            return i

    # Column not found with 06-Mar
    assert False


def gmt_start_time_row():
    return 4


def gmt_stop_time_row():
    return 5


def gmt_date_row():
    return 3
