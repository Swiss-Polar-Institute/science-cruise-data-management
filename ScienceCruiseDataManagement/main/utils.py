import datetime
import unicodedata
import math

from django.db.models.query import EmptyQuerySet
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
from django.core.exceptions import ObjectDoesNotExist

import csv

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

class Location:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.date_time = None
        self.device = None
        self.is_valid = True

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
    if not user.has_perm(main.models.cannot_change[0][0]):
        return False

    return True


def latest_ship_position():
    try:
        gps = SamplingMethod.objects.get(name=settings.MAIN_GPS)
    except ObjectDoesNotExist:
        return Location()

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

    # Raw query set doesn't have .exists() or ._len_
    for position in position_main_gps_query:
        if abs(position.date_time - date_time).seconds <= 5:
            return True

    return False


def set_utc(date_time):
    utc = datetime.timezone(datetime.timedelta(0))
    date_time = date_time.replace(tzinfo=utc)
    return date_time


def last_midnight():
    date_time = datetime.datetime.utcnow()
    date_time = set_utc(date_time)

    day = datetime.timedelta(days=1)
    date_time = date_time - day
    last_midnight_date_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59)

    last_midnight_date_time = set_utc(last_midnight_date_time)
    return last_midnight_date_time


def ship_location(date_time):
    main_gps = SamplingMethod.objects.get(name=settings.MAIN_GPS)
    main_gps_id = main_gps.id

    # It uses objects.raw so Mysql is using the right index (datetime). The CAST is what it
    # makes it to use, USE INDEX() is not needed.
    valid_measureland_ids = ",".join(valid_measureland_qualifier_ids())
    position_main_gps_query = GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time > cast(%s as datetime) and ship_data_gpggagpsfix.device_id=%s and ship_data_gpggagpsfix.measureland_qualifier_flags_id in ({}) ORDER BY date_time LIMIT 1'.format(valid_measureland_ids), [date_time, main_gps_id])
    position_any_gps_query =  GpggaGpsFix.objects.raw('SELECT * FROM ship_data_gpggagpsfix WHERE ship_data_gpggagpsfix.date_time > cast(%s as datetime) and ship_data_gpggagpsfix.measureland_qualifier_flags_id in ({}) ORDER BY date_time LIMIT 1'.format(valid_measureland_ids), [date_time])

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
        location = Location()
        location.is_valid = False
        return location
    else:
        location = Location()
        if not is_correct_position(position):
            location.is_valid = False
            return location

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
    print("Exporting to file:", file_path)
    file = open(file_path + ".tmp", "w")

    csv_writer = csv.writer(file)

    fields = model._meta.get_fields()
    field_names = [f.name for f in fields]
    field_names.remove('id')

    csv_writer.writerow(field_names)

    current_date = first_date
    one_day = datetime.timedelta(days=1)

    while current_date <= last_date:
        print("Processing:", current_date.strftime("%Y-%m-%d"), "Last date:", last_date.strftime("%Y-%m-%d"))
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
    os.rename(file_path + ".tmp", file_path)


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


def rfc3339_to_datetime(rfc3339):
    return set_utc(datetime.datetime.strptime(rfc3339, "%Y-%m-%d %H:%M:%S"))


def filter_events_success_or_failure():
    filter_query = Q(outcome='Success') | Q(outcome='Failure')

    return filter_query


def filter_open_events():
    filter_query = Q(number=0)  # Impossible with OR will be the rest

    for open_event in main.models.OpenEvent.objects.all():
        filter_query = filter_query | Q(number=open_event.number)

    return filter_query


def calculate_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371*1000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
                                                  * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d


def wrong_data_measureland_qualifier_flags():
    return ["probably bad value", "bad value", "value below detection", "value in excess", "value phenomenon uncertain"]

def valid_measureland_qualifier_ids():
    valid_ids = []

    for measureland in main.models.MeasurelandQualifierFlags.objects.all():
        if measureland.preferred_label not in wrong_data_measureland_qualifier_flags():
            valid_ids.append(str(measureland.id))

    return valid_ids

def filter_in_bad_values():
    q = None
    for label in wrong_data_measureland_qualifier_flags():
        if q is None:
            q = Q(measureland_qualifier_flags__preferred_label=label)
        else:
            q |= Q(measureland_qualifier_flags__preferred_label=label)

    return q


def filter_out_bad_values():
    q = None
    for avoid_label in wrong_data_measureland_qualifier_flags():
        if q is None:
            q = ~Q(measureland_qualifier_flags__preferred_label=avoid_label)
        else:
            q &= ~Q(measureland_qualifier_flags__preferred_label=avoid_label)

    return q


def is_correct_position(gpgga_gps_fix):
    return not (gpgga_gps_fix.measureland_qualifier_flags.preferred_label in wrong_data_measureland_qualifier_flags())