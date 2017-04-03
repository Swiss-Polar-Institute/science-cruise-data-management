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
        elif options['action'] == "analysegps":
            gps = SamplingMethod.objects.get(name=options["gps1"])

            analyse(gps)


def analyse(gps):
    print("gps:", gps)

    earliest = GpggaGpsFix.objects.filter(device=gps).earliest()
    latest_date_time = GpggaGpsFix.objects.filter(device=gps).latest().date_time

    current_date = earliest.date_time

    count = 0
    previous_position = gpggagpsfix_to_location(earliest)

    while current_date <= latest_date_time:
        print("Analysing 24 hours from:", current_date)
        day_after = current_date + datetime.timedelta(days=1)

        positions = GpggaGpsFix.objects.filter(device=gps).filter(date_time__gte=current_date).filter(date_time__lt=day_after).order_by("date_time")

        for position in positions:
            current_position = gpggagpsfix_to_location(position)

            knots = knots_two_points(previous_position, current_position)

            error_message = ""

            if knots == "N/A":
                error_message = "No speed?"
            elif knots >= 20:
                error_message += "**** Too fast"

            if error_message != "":
                print("{}           ({:.2f} {:.2f})".format(previous_position.date_time,
                                                           current_position.latitude, current_position.longitude))

                print("{} {} knots  ({:.2f} {:.2f})".format(current_position.date_time, knots,
                                                           current_position.latitude, current_position.longitude))

            previous_position = current_position

        current_date = day_after

    print("Total:", count)


def knots_two_points(location1, location2):
    distance = utils.calculate_distance((location1.latitude, location1.longitude),
                                        (location2.latitude, location2.longitude))

    seconds = abs((location1.date_time - location2.date_time).total_seconds())

    if seconds > 0:
        return (distance/seconds) * 1.9438
    else:
        return "N/A"


def compare_gps(gps1, gps2):
    earliest_gps1 = GpggaGpsFix.objects.filter(device=gps1).earliest()
    earliest_gps2 = GpggaGpsFix.objects.filter(device=gps2).earliest()

    earliest_date_gps1 = earliest_gps1.date_time
    earliest_date_gps2 = earliest_gps2.date_time

    latest_date_gps1 = GpggaGpsFix.objects.filter(device=gps1).latest().date_time
    latest_date_gps2 = GpggaGpsFix.objects.filter(device=gps2).latest().date_time

    delta_time = datetime.timedelta(seconds=60)

    earliest_date = max(earliest_date_gps1, earliest_date_gps2)
    latest_date = min(latest_date_gps1, latest_date_gps2)

    current_date = earliest_date + datetime.timedelta(seconds=60)

    gps1_previous_location = ship_location(current_date, gps1)
    gps2_previous_location = ship_location(current_date, gps2)

    while current_date < latest_date:
        current_date += delta_time

        gps1_location = ship_location(current_date, gps1)
        gps2_location = ship_location(current_date, gps2)

        if gps1_location is not None and gps1_previous_location is not None:
            speed_gps1 = "{:.2f}".format(knots_two_points(gps1_previous_location, gps1_location))
            date_time_gps1 = gps1_location.date_time.strftime("%Y-%m-%d %H:%M:%S")
            position_gps1 = "({:.2f}, {:.2f})".format(gps1_location.latitude, gps1_location.longitude)

        else:
            # print("Date: {} no information for GPS: {}".format(current_date, gps1.name))
            speed_gps1 = "N/A"
            date_time_gps1 = "N/A"

        if gps2_location is not None and gps2_previous_location is not None:
            speed_gps2 = "{:.2f}".format(knots_two_points(gps2_previous_location, gps2_location))
            date_time_gps2 = gps2_location.date_time.strftime("%Y-%m-%d %H:%M:%S")
            position_gps2 = "({:.2f}, {:.2f})".format(gps2_location.latitude, gps2_location.longitude)

        else:
            # print("Date: {} no information for GPS: {}".format(current_date, gps2.name))
            speed_gps2 = "N/A"
            date_time_gps2 = "N/A"



        if gps1_location is not None and gps2_location is not None:
            distance = utils.calculate_distance((gps1_location.latitude, gps1_location.longitude),
                                          (gps2_location.latitude, gps2_location.longitude))

            if distance is not None:
                distance = "{:.2f}".format(distance)
            else:
                distance = "N/A"


        warning = ""

        try:
            kn1 = float(speed_gps1)
            kn2 = float(speed_gps2)
            meters = float(distance)

            if kn1 > 20:
                warning += "**** kn1"

            if kn2 > 20:
                warning += "**** kn2"

            if (meters < 5 or meters > 35) and (meters > 0.0001 and meters < 0.0001):
                warning += "**** meters"

        except ValueError:
            pass



        print("{}: {} m\t{} knots\t{} knots\t{}\t{}\t{}\t{}\t{}".format(current_date, distance,
                                                                 speed_gps1, speed_gps2,
                                                                 date_time_gps1,
                                                                 date_time_gps2,
                                                                 position_gps1,
                                                                 position_gps2,
                                                                 warning))

        gps1_previous_location = gps1_location
        gps2_previous_location = gps2_location


def gpggagpsfix_to_location(gpggagpsfix):
    location = utils.Location()

    location.date_time = gpggagpsfix.date_time
    location.latitude = gpggagpsfix.latitude
    location.longitude = gpggagpsfix.longitude
    location.device = gpggagpsfix.device

    return location

def ship_location(date_time, device):
    # It uses objects.raw so Mysql is using the right index (datetime). The CAST is what it
    # makes it to use, USE INDEX() is not needed.
    position_gps_query = GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time >= cast(%s as datetime) and ship_data_gpggagpsfix.device_id=%s ORDER BY date_time LIMIT 1', [date_time, device.id])

    position_gps_query = position_gps_query[0]

    if abs(position_gps_query.date_time - date_time) > datetime.timedelta(seconds=10):
        return None
    else:
        location = gpggagpsfix_to_location(position_gps_query)
        return location