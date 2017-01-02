import datetime

from django.conf import settings
import main.models
from main.models import ParentDevice
from ship_data.models import GpggaGpsFix


class Location:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.date_time = None
        self.device = None

    def formatted_latitude(self):
        return "{:.4f}".format(self.latitude)

    def formatted_longitude(self):
        return "{:.4f}".format(self.longitude)

def can_user_change_events(path, user):
    # To make sure that the user can edit events
    if path.endswith("/add/"):
        return True

    # But if it's not /add/, if the user is in the "Add Events"
    # should not be able to change them
    for permission in main.models.cannot_change_events_all:
        if not user.has_perm(permission[0][0]):
            return False

    return True


def latest_ship_position():
    gps = ParentDevice.objects.get(name=settings.MAIN_GPS)
    positions = GpggaGpsFix.objects.filter(device=gps).order_by('-date_time')

    if positions.exists():
        position = positions[0]
        location = Location()
        location.latitude = position.latitude
        location.longitude = position.longitude
        location.date_time = position.date_time
        location.device = gps

        return location
    else:
        return Location()


def string_to_date_time(date_time_string):
    try:
        date_time = datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            date_time = datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M")
        except ValueError:
            date_time = None

    if date_time is not None:
        utc = datetime.timezone(datetime.timedelta(0))
        date_time = date_time.replace(tzinfo=utc)

    return date_time


def now_with_timezone():
    now = datetime.datetime.now()
    utc = datetime.timezone(datetime.timedelta(0))
    now = now.replace(tzinfo=utc)

    return now


def ship_location(date_time):
    gps = ParentDevice.objects.get(name=settings.MAIN_GPS)
    position_main_gps_query = GpggaGpsFix.objects.filter(device=gps).filter(date_time__gt=date_time).order_by('date_time')
    position_any_gps_query = GpggaGpsFix.objects.filter(date_time__gt=date_time).order_by('date_time')

    device = None
    if position_main_gps_query.exists():
        position_main_gps = position_main_gps_query[0]
        seconds_difference_main_gps = abs(date_time - position_main_gps.date_time).total_seconds()
    else:
        position_main_gps = None
        seconds_difference_main_gps = 99999

    if position_any_gps_query.exists():
        position_any_gps = position_any_gps_query[0]
        seconds_difference_any_gps = abs(date_time - position_any_gps.date_time).total_seconds()
    else:
        position_any_gps = None
        seconds_difference_any_gps = 99999

    if seconds_difference_main_gps < 60:
        position = position_main_gps
        device = position_main_gps.device
    elif seconds_difference_any_gps < 60:
        position = position_any_gps
        device = position_any_gps.device
    else:
        position = None

    if position is None:
        return Location()
    else:
        location = Location()
        location.latitude = position.latitude
        location.longitude = position.longitude
        location.date_time = position.date_time
        location.device = device

        return location
