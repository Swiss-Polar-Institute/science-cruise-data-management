import datetime

from django.conf import settings
import main.models
from main.models import ParentDevice
from ship_data.models import GpggaGpsFix

from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth.models import User
from django.contrib.admin.options import get_content_type_for_model


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
    main_gps = ParentDevice.objects.get(name=settings.MAIN_GPS)
    main_gps_id = main_gps.id

    # It uses objects.raw so Mysql is using the right index (datetime). The CAST is what it
    # makes it to use, USE INDEX() is not needed.
    position_main_gps_query = GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time > cast(%s as datetime) and ship_data_gpggagpsfix.device_id=%s ORDER BY date_time LIMIT 1', [date_time, main_gps_id])
    position_any_gps_query =  GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time > cast(%s as datetime) ORDER BY date_time LIMIT 1', [date_time])

    device = None

    try:
        position_main_gps = position_main_gps_query[0]
    except IndexError:
        position_main_gps = None

    if position_main_gps:
        seconds_difference_main_gps = abs(date_time - position_main_gps.date_time).total_seconds()
    else:
        position_main_gps = None
        seconds_difference_main_gps = 99999

    try:
        position_any_gps = position_any_gps_query[0]
    except IndexError:
        position_any_gps = None

    if position_any_gps:
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


def object_model_created_by(obj):
    content_type_id = get_content_type_for_model(obj).pk
    object_id = obj.pk
    log_entry_queryset = LogEntry.objects.filter(action_flag=ADDITION).filter(content_type_id=content_type_id).filter(action_flag=ADDITION).filter(object_id=object_id)

    if len(log_entry_queryset) == 1:
        user_id = log_entry_queryset[0].user_id

        user_queryset = User.objects.filter(id=user_id)

        if len(user_queryset) == 1:
            return user_queryset[0].username

    return "Unknown"
