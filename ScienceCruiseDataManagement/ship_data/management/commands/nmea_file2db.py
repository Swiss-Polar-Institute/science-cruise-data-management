from django.core.management.base import BaseCommand, CommandError

from ship_data.models import GpzdaDateTime, GpggaGpsFix, GpvtgVelocity
from main.models import SamplingMethod
import time
from ship_data import utilities
import os
import datetime
import traceback

class Command(BaseCommand):
    help = 'Reads the NMEA data and writes it into the database. Keeps checking for new files.'

    def add_arguments(self, parser):
        parser.add_argument('device', type=str,
                            action='store',
                            help='A SamplingMethod table name that is the source of this file')
        parser.add_argument('directory_path', type=str,
                            action='store',
                            help='Directory where to fetch the files from')
        parser.add_argument('--start-file', type=str,
                            action='store',
                            dest='start_file',
                            default=None,
                            help='Which file should start with in an ordered way')

    def handle(self, *args, **options):
        process = ProcessNMEAFile(options['device'], options['directory_path'], options['start_file'])
        process.process()


class ProcessNMEAFile:
    def __init__(self, device_string, directory, start_file):
        self.device_string = device_string
        self.device = None
        self.directory = directory
        self.start_file = start_file
        self.last_datetime = None
        self.utc = datetime.timezone(datetime.timedelta(0))

    def process(self):
        if not SamplingMethod.objects.filter(name=self.device_string).exists():
            print("Error: sampling method type {} doesn't exist in the SamplingMethod table".format(self.device_string))
            exit(1)

        self.device = SamplingMethod.objects.get(name=self.device_string)

        tail_directory = TailDirectory(self.directory, self.start_file, self._process_line)
        tail_directory.read_all_directory()

    def _process_line(self, line):
        if line.startswith("$GPZDA,"):
            self._import_gpzda(line)
        elif line.startswith("$GPGGA,"):
            self._import_gpgga(line)
        elif line.startswith("$GPVTG,"):
            self._import_gpvtg(line)
        else:
            pass

    def _string_time_to_tuple(time_string):
        hour = int(time_string[0:2])
        minute = int(time_string[2:4])
        seconds = int(time_string[4:6])

        # Some GPS sources have the time with hundreds of seconds like.
        # HHMMSS.tt . Some don't have the ".tt"
        if "." in time_string:
            millions_of_sec = int(time_string.split(".")[1])*10000
        else:
            millions_of_sec = 0

        return (hour, minute, seconds, millions_of_sec)


    def _import_gpzda(self, line):
        try:
            (nmea_reference, time_with_hundreds_sec, day, month, year, local_zone_hours, min_checksum) = line.split(",")
            (local_zone_minutes, checksum) = min_checksum.split("*")
        except ValueError as e:
            print("Exception: {}".format(e))
            print("Error unpacking: {}".format(line))
            traceback.print_exc()
            return

        year = int(year)
        month = int(month)
        day = int(day)

        (hour, minute, second, millions_of_sec) = ProcessNMEAFile._string_time_to_tuple(time_with_hundreds_sec)
        date_time = datetime.datetime(year, month, day, hour, minute, second, millions_of_sec, self.utc)

        self.last_datetime = date_time

        gpzda = GpzdaDateTime()

        gpzda.device = self.device

        gpzda.device = self.device
        gpzda.date_time = date_time
        gpzda.day = day
        gpzda.month = month
        gpzda.year = year
        gpzda.local_zone_hours = int(local_zone_hours)
        gpzda.local_zone_minutes = int(local_zone_minutes)

        if not GpzdaDateTime.objects.filter(date_time=date_time, device=self.device).exists():
            gpzda.save()

    def _current_date_time_smaller_than_before(self, time_string):
        return self._current_date_time(time_string) < self.last_datetime

    def _current_date_time(self, time_string):
        (hour, minute, second, millions_of_sec) = ProcessNMEAFile._string_time_to_tuple(time_string)
        current_date_time = datetime.datetime(self.last_datetime.year, self.last_datetime.month,
                                              self.last_datetime.day, hour, minute, second, millions_of_sec, self.utc)

        return current_date_time

    def _import_gpgga(self, line):
        if self.last_datetime is None:
            # If this is the first line of the file last_datetime would be None and we skip it
            # it doesn't have it
            return

        try:
            (nmea_reference, time_string, nmea_latitude, nmea_latitude_ns, nmea_longitude, nmea_longitude_ew,
             fix_quality, number_satellites, horizontal_diluation_of_position,
             altitude, altitude_units, geoid_height, geoid_height_units,
             something, checksum) = line.split(",")
        except ValueError as e:
            print("Exception: {}".format(e))
            print("Error unpacking: {}".format(line))
            traceback.print_exc()
            return

        (latitude, longitude) = utilities.nmea_lat_long_to_normal(nmea_latitude, nmea_latitude_ns, nmea_longitude, nmea_longitude_ew)

        gps_fix = GpggaGpsFix()

        # Here it will check if the "guessed" date_time for the current line is earlier than
        # the last one. If this is the case it doesn't do anything: probably we've missed
        # (corrupted data?) a line with the complete date. Note that this line doesn't have the
        # date, only the hour
        if self._current_date_time_smaller_than_before(time_string):
            print("Oops, time went backwards for import_gpgga, not inserting line: {}".format(line))
            return

        current_date_time = self._current_date_time(time_string)

        gps_fix.device = self.device
        gps_fix.date_time = current_date_time
        gps_fix.latitude = latitude
        gps_fix.longitude = longitude
        gps_fix.fix_quality = fix_quality
        gps_fix.number_satellites = number_satellites
        gps_fix.horiz_dilution_of_position = horizontal_diluation_of_position
        gps_fix.altitude = altitude
        gps_fix.altitude_units = altitude_units

        if geoid_height!= '' and geoid_height_units != '':
            gps_fix.geoid_height = geoid_height
            gps_fix.geoid_height_units = geoid_height_units

        if not GpggaGpsFix.objects.filter(date_time=current_date_time, device=self.device).exists():
            gps_fix.save()

    def _import_gpvtg(self, line):
        if self.last_datetime is None:
            # If this is the first line of the file last_datetime would be None and we skip it
            # it doesn't have it
            return

        try:
            (nmea_reference, true_track_deg, t, magnetic_track_deg, m, ground_speed_kts, n, ground_speed_kmh, k, something) = line.split(",")
        except ValueError as e:
            print("Exception: {}".format(e))
            print("Error unpacking: {}".format(line))
            traceback.print_exc()
            return

        if t != "T":
            print("t field is not T?", line)

        if m != "M":
            print("m field is not M?", line)

        if n!= "N":
            print("n field is not N?", line)

        if k != "K":
            print("k field is not K?", line)

        velocity = GpvtgVelocity()

        velocity.device = self.device
        date_time = self.last_datetime
        velocity.date_time = date_time
        velocity.true_track_deg = true_track_deg

        if magnetic_track_deg != '':
            velocity.magnetic_track_deg = magnetic_track_deg

        velocity.ground_speed_kts = ground_speed_kts

        if not GpvtgVelocity.objects.filter(date_time=date_time, device=self.device):
            velocity.save()


class TailDirectory:
    def __init__(self, directory, start_file, callback):
        self.directory = directory
        if start_file is not None:
            self.current_file = os.path.join(self.directory, start_file)
        else:
            self.current_file = None

        self.SLEEP_INTERVAL = 0.5   # for when new lines keep appearing
        self.callback = callback

    def read_all_directory(self):
        if self.current_file is None:
            self.current_file = self._find_first_file()

        while True:                 # it can always be more data
            file = open(self.current_file, "r")

            self._process_existing_lines(file)
            self._process_new_lines(file)         # will change the self.current_file when needed

    def _process_existing_lines(self, file):
        print("Will process existing lines for:", self.current_file)
        while True:
            where = file.tell()

            try:
                line = file.readline()
            except UnicodeDecodeError:
                continue

            if not line.endswith("\n"):
                # We've read a partial line, so we are at the end of the file
                # We rewind to the beginning of the line and then will pass to the
                # process_new_lines
                file.seek(where)
                return

            if line == "":
                return

            line = line.rstrip()
            self.callback(line)

    def _process_new_lines(self, file):
        print("Will process new lines for:", self.current_file)
        while True:
            where = file.tell()

            try:
                line = file.readline()
            except UnicodeDecodeError:
                print("Unicode error, will skip")
                continue

            if (len(line) > 0) and (line.endswith("\n") == False):
                # To make sure that we haven't read a partial line at the end of the file
                print("Partial line read, will retry: _{}_".format(line))
                file.seek(where)
                time.sleep(self.SLEEP_INTERVAL)
                continue

            if not line:
                file.seek(where)
                time.sleep(self.SLEEP_INTERVAL)
                next_file = self._find_next_file()

                if next_file is not None and next_file != self.current_file:
                    # We move to a new file
                    print("Will move from {} to {}".format(self.current_file, next_file))
                    self.current_file = next_file
                    return
            else:
                line = line.rstrip()
                self.callback(line)


    def _find_first_file(self):
        files = os.listdir(self.directory)

        if len(files) == 0:
            print("There are no files in the",self.directory,"directory. Aborting")
            exit(1)

        files.sort()
        return os.path.join(self.directory,files[0])

    def _find_next_file(self):
        """ Returns the next file that needs to be read or None if it's the current file. """

        files_in_directory = os.listdir(self.directory)
        files_in_directory.sort()

        if self.current_file is None:
            return os.path.join(self.directory, files_in_directory[0])

        for file in files_in_directory:
            file = os.path.join(self.directory, file)

            if file > self.current_file:
                return file

        return None