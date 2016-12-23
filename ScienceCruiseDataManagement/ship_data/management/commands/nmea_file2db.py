from django.core.management.base import BaseCommand, CommandError
from gpxpy.gpxfield import gpx_check_slots_and_default_values

from ship_data.models import GpzdaDateTime, GpggaGpsFix, GpvtgVelocity
import time
from ship_data import utilities


class Command(BaseCommand):
    help = 'Reads the NMEA data and writes it into the database'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        process = ProcessNMEAFile(options['path'])
        process.process()


class ProcessNMEAFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_datetime = None

    def process(self):
        tail_file = TailFile(self.file_path, self._process_line)
        tail_file.readlines_then_tail()

    def _process_line(self, line):
        if line.startswith("$GPZDA,"):
            self.import_gpzda(line)
        elif line.startswith("$GPGGA,"):
            self.import_gpgga(line)
        elif line.startswith("$GPVTG,"):
            self.import_gpvtg(line)
        else:
            print("Ignoring line", line)

    def import_gpzda(self, line):
        (nmea_reference, date_time, day, month, year, local_zone_hours, min_checksum) = line.split(",")
        (local_zone_minutes, checksum) = min_checksum.split("*")

        self.last_datetime = date_time

        gpzda = {}
        gpzda['time'] = date_time
        gpzda['day'] = int(day)
        gpzda['month'] = int(month)
        gpzda['year'] = int(year)
        gpzda['local_zone_hours'] = int(local_zone_hours)
        gpzda['local_zone_minutes'] = int(local_zone_minutes)

        GpzdaDateTime.objects.update_or_create(time=date_time, defaults=gpzda)

    def import_gpgga(self, line):
        (nmea_reference, date_time, nmea_latitude, nmea_latitude_ns, nmea_longitude, nmea_longitude_ew,
         fix_quality, number_satellites, horizontal_diluation_of_position,
         altitude, altitude_units, geoid_height, geoid_height_units,
         something, checksum) = line.split(",")

        self.last_datetime = date_time

        (latitude, longitude) = utilities.nmea_lat_long_to_normal(nmea_latitude, nmea_latitude_ns, nmea_longitude, nmea_longitude_ew)

        gps_fix = {}
        gps_fix["time"] = date_time
        gps_fix["latitude"] = latitude
        gps_fix["longitude"] = longitude
        gps_fix["fix_quality"] = fix_quality
        gps_fix["number_satellites"] = number_satellites
        gps_fix["horiz_dilution_of_position"] = horizontal_diluation_of_position
        gps_fix["altitude"] = altitude
        gps_fix["altitude_units"] = altitude_units
        gps_fix["geoid_height"] = geoid_height
        gps_fix["geoid_height_units"] = geoid_height_units

        GpggaGpsFix.objects.update_or_create(time=date_time, defaults=gps_fix)

    def import_gpvtg(self, line):
        if self.last_datetime is None:
            # If this is the first line of the file last_datetime would be None and we skip it
            # it doesn't have it
            return

        (nmea_reference, true_track_deg, t, magnetic_track_deg, m, ground_speed_nautical, n, ground_speed_knots, k, something) = line.split(",")

        if t != "T":
            print("t field is not T?", line)

        if m != "M":
            print("m field is not M?", line)

        if n!= "N":
            print("n field is not N?", line)

        if k != "K":
            print("k field is not K?", line)

        velocity = {}
        velocity["time"] = self.last_datetime
        velocity["true_track_deg"] = true_track_deg
        velocity["magnetic_track_deg"] = magnetic_track_deg
        velocity["ground_speed_kts"] = ground_speed_knots

        GpvtgVelocity.objects.update_or_create(time=time, defaults=velocity)


class TailFile:
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.SLEEP_INTERVAL = 0.5
        self.callback = callback

    def readlines_then_tail(self):
        """ Yields all the lines of the file and then starts tailing. """

        file = open(self.file_path, "r")

        for line in self._yield_lines(file):
            line = line.rstrip()
            print(line)
            self.callback(line)

    def _yield_lines(self, file):
        while True:
            try:
                line = file.readline()
            except UnicodeDecodeError:
                yield ""

            if line:
                yield line
            else:
                yield self._tail(file)

    def _tail(self, file):
        while True:
            where = file.tell()
            line = file.readline()
            if not line:
                time.sleep(self.SLEEP_INTERVAL)
                file.seek(where)
            else:
                return line
