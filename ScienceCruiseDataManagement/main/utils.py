import datetime
import unicodedata

from django.db import connection
from django.conf import settings
import main.models
import shutil
import os
from main.models import SamplingMethod
from ship_data.models import GpggaGpsFix
import re

from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth.models import User
from django.contrib.admin.options import get_content_type_for_model
from django.forms.models import model_to_dict
from django.db.models import Q

import csv


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
    gps = SamplingMethod.objects.get(name=settings.MAIN_GPS)
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


def string_to_date_time_format(date_time_string, format):
    try:
        return datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def string_to_date_time(date_time_string):
    possible_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"]

    date_time = None
    for format in possible_formats:
        try:
            date_time = datetime.datetime.strptime(date_time_string, format)
        except ValueError:
            pass

    if date_time is not None:
        utc = datetime.timezone(datetime.timedelta(0))
        date_time = date_time.replace(tzinfo=utc)

    return date_time


def now_with_timezone():
    now = datetime.datetime.now()
    utc = datetime.timezone(datetime.timedelta(0))
    now = now.replace(tzinfo=utc)

    return now


def ship_location_exists(date_time, device_id):
    position_main_gps_query = GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time > cast(%s as datetime) and ship_data_gpggagpsfix.device_id=%s ORDER BY date_time LIMIT 1', [date_time, device_id])

    if abs(position_main_gps_query[0].date_time - date_time).seconds <= 5:
        # Yes data in between 5 seconds
        return True
    else:
        # No data
        return False


def set_utc(date_time):
    utc = datetime.timezone(datetime.timedelta(0))
    date_time = date_time.replace(tzinfo=utc)
    return date_time


def last_midnight(date_time):
    day = datetime.timedelta(1)
    date_time = date_time - day
    last_midnight_date_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59)

    last_midnight_date_time = set_utc(last_midnight_date_time)
    return last_midnight_date_time


def ship_location(date_time):
    main_gps = SamplingMethod.objects.get(name=settings.MAIN_GPS)
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


def find_object(obj, field, name):
    queryset = obj.objects.filter(**{field: name})

    if len(queryset) == 1:
        return queryset[0]
    else:
        return None


def move_imported_file(original_directory_name, filename):
    shutil.move(original_directory_name + "/" + filename, original_directory_name + "/../uploaded")


def add_imported(filepath, object_type):
    basename = os.path.basename(filepath)
    dirname = os.path.dirname(filepath)

    file = main.models.ImportedFile()
    file.file_name = basename
    file.date_imported = datetime.datetime.utcnow()

    utc = datetime.timezone(datetime.timedelta(0))
    file.date_imported = file.date_imported.replace(tzinfo=utc)

    file.object_type = object_type

    file.save()
    move_imported_file(dirname, basename)
    print(basename, " moved from ", dirname)


def export_table(model, file_path, first_date, last_date):
    file = open(file_path, "w")

    csv_writer = csv.writer(file)

    fields = model._meta.get_fields()
    field_names = [f.name for f in fields]
    field_names.remove('id')

    csv_writer.writerow(field_names)

    current_date = first_date
    one_day = datetime.timedelta(days=1)

    while current_date <= last_date:
        current_date_tomorrow = current_date + one_day
        met_data_all = model.objects.filter(Q(date_time__gte=current_date) & Q(date_time__lt=current_date_tomorrow)).order_by('date_time')
        for met_data in met_data_all:
            row = []
            met_data_dictionary = model_to_dict(met_data)

            for field_name in field_names:
                row.append(met_data_dictionary[field_name])

            csv_writer.writerow(row)

        current_date += one_day

    file.close()


def sql_row_to_dictionary(sql_row, field_names):
    d = {}

    for (index, field_name) in enumerate(field_names):
        d[field_name] = sql_row[index]

    return d


def normalised_csv_file(file_path):
    """Returns the text of the file replacing \t with , removing empty lines, etc.
       to be processed by the csv module.
    """
    file_contents = open(file_path).read()

    file_contents = file_contents.replace("\t", ",")

    file_contents = re.sub(r'    \n', '\n', file_contents)

    previous = ""

    while previous != file_contents:
        previous = file_contents
        file_contents = file_contents.replace("\n\n", "\n")

    return file_contents


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

