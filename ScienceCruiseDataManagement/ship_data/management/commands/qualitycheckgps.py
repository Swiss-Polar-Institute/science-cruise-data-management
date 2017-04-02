from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
from main.models import SamplingMethod
import subprocess
import datetime
from main import utils


class Command(BaseCommand):
    help = 'Ferrybox data'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help="Can be checkspeed or comparegps")
        parser.add_argument('--gps1', type=str)
        parser.add_argument('--gps2', type=str)

    def handle(self, *args, **options):
        if options['action'] == "comparegps":
            gps1 = SamplingMethod.objects.get(name=options["gps1"])
            gps2 = SamplingMethod.objects.get(name=options["gps2"])

            compare_gps(gps1, gps2)


def compare_gps(gps1, gps2):
    earliest_date_gps1 = GpggaGpsFix.objects.filter(device=gps1).earliest().date_time
    earliest_date_gps2 = GpggaGpsFix.objects.filter(device=gps2).earliest().date_time

    latest_date_gps1 = GpggaGpsFix.objects.filter(device=gps1).latest().date_time
    latest_date_gps2 = GpggaGpsFix.objects.filter(device=gps2).latest().date_time

    delta_time = datetime.timedelta(seconds=600)

    earliest_date = max(earliest_date_gps1, earliest_date_gps2)
    latest_date = min(latest_date_gps1, latest_date_gps2)

    current_date = earliest_date

    while current_date < latest_date:
        current_date += delta_time

        gps1_location = ship_location(current_date, gps1)
        gps2_location = ship_location(current_date, gps2)

        if gps1_location is None:
            print("Date: {} no information for GPS: {}".format(current_date, gps1.name))
            continue

        if gps2_location is None:
            print("Date: {} no information for GPS: {}".format(current_date, gps2.name))
            continue

        distance = 1000 * utils.calculate_distance((gps1_location.latitude, gps1_location.longitude),
                                      (gps2_location.latitude, gps2_location.longitude))

        print("{}: {}".format(current_date, distance))


def ship_location(date_time, device):
    # It uses objects.raw so Mysql is using the right index (datetime). The CAST is what it
    # makes it to use, USE INDEX() is not needed.
    position_gps_query = GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time >= cast(%s as datetime) and ship_data_gpggagpsfix.device_id=%s ORDER BY date_time LIMIT 1', [date_time, device.id])

    position_gps_query = position_gps_query[0]

    if abs(position_gps_query.date_time - date_time) > datetime.timedelta(seconds=10):
        return None
    else:
        location = utils.Location()
        location.date_time = position_gps_query.date_time
        location.latitude = position_gps_query.latitude
        location.longitude = position_gps_query.longitude
        location.device = device

        return location