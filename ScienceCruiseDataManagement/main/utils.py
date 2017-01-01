import datetime

from django.conf import settings
import main.models
from main.models import ParentDevice
from ship_data.models import GpggaGpsFix


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
    gps = ParentDevice.objects.all().get(name=settings.MAIN_GPS)
    positions = GpggaGpsFix.objects.all().filter(device=gps).order_by('-date_time')

    if positions.exists():
        position = positions[0]
        return (position.latitude, position.longitude, position.date_time)
    else:
        return (None, None, None)


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