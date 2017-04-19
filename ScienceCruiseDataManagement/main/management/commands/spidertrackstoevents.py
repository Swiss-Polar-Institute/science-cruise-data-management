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

class Track:
    aircraft = None
    start_time = None
    start_latitude = None
    start_longitude = None
    end_time = None
    end_latitude = None
    end_longitude = None
    latest_point = None
    is_valid = False
    start_line = None


class Command(BaseCommand):
    help = 'Converts a spider tracks spreadsheet to events one (so then it can be imported)'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        convert_spreadsheet(options['filename'])


def read_tracks(input_filename):
    csv_reader = csv.DictReader(open(input_filename, encoding='utf-8', errors='ignore'))

    tracks = []

    active_tracks = {}

    spreadsheet_row = 1
    for line in csv_reader:
        spreadsheet_row += 1

        aircraft = line['Aicraft']

        date_time = line['DateTime(UTC)']
        latitude = float(line['Latitude(decimal)'])
        longitude = float(line['Longitude(decimal)'])
        point = int(line['Point'])

        if point == 1:
            track = Track()
            track.aircraft = aircraft

            if aircraft == "G-TVAM":
                track.sampling_method = "Spidertracks G-TVAM"
            elif aircraft == "G-BATC":
                track.sampling_method = "Spidertracks G-BATC"
            else:
                assert False

            track.start_time = date_time
            track.start_latitude = "{:.4f}".format(latitude)
            track.start_longitude = "{:.4f}".format(longitude)
            track.end_time = date_time
            track.end_latitude = "{:.4f}".format(latitude)
            track.end_longitude = "{:.4f}".format(longitude)
            track.latest_point = point
            track.first_line_spreadsheet = spreadsheet_row

            active_tracks[aircraft] = track
            tracks.append(track)

        else:
            current_track = active_tracks[aircraft]
            current_track.end_time = date_time
            current_track.end_latitude = "{:.4f}".format(latitude)
            current_track.end_longitude = "{:.4f}".format(longitude)
            assert point == (current_track.latest_point + 1)
            current_track.latest_point = point

            if int(line['Altitude(ft)']) > 100:
                current_track.is_valid = True

    return tracks


def write_tracks(output_filename, tracks):
    csv_writer = csv.DictWriter(open(output_filename, "w"),
                                ['sampling_method', 'data', 'samples', 'start_time', 'type', 'what_happened_start',
                                 'end_time', 'type', 'what_happened_end', 'time_source', 'time_uncertainty',
                                 'general_comments', 'start_latitude', 'start_longitude', 'end_latitude',
                                 'end_longitude', 'position_source', 'position_uncertainty'])

    csv_writer.writeheader()

    for track in tracks:
        if not track.is_valid:
            print("Not valid track starting at line:", track.first_line_spreadsheet)
            continue

        d = {}
        d['sampling_method'] = track.sampling_method
        d['data'] = 'True'
        d['samples'] = 'False'
        d['start_time'] = track.start_time
        d['type'] = 'Begins'
        d['what_happened_start'] = 'started'
        d['end_time'] = track.end_time
        d['type'] = 'Ends'
        d['what_happened_end'] = 'stopped'
        d['time_source'] = 'Spider track instrument'
        d['time_uncertainty'] = 'Milliseconds'
        d['general_comments'] = ''
        d['start_latitude'] = track.start_latitude
        d['start_longitude'] = track.start_longitude
        d['end_latitude'] = track.end_latitude
        d['end_longitude'] = track.end_longitude
        d['position_source'] = 'Spider track instrument'
        d['position_uncertainty'] = '0.0 to 0.01 n.miles'

        csv_writer.writerow(d)


def convert_spreadsheet(input_filename):
    new_filename = os.path.basename(input_filename)

    new_path = os.path.dirname(input_filename)
    new_filename = "Events-" + new_filename

    new_filepath = os.path.join(new_path, new_filename)

    tracks = read_tracks(input_filename)

    write_tracks(new_filepath, tracks)
    print("Spreadsheet as event format as", new_filepath)