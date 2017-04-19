from django.core.management.base import BaseCommand, CommandError
from ship_data.models import MetDataAll, MetDataWind
from main import utils
import os
import shutil
import re
import datetime
import glob
import csv
from django.db.models import Avg, F
from django.db.models import Q

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

class Command(BaseCommand):
    help = 'Outputs the Met data in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str, help="Output directory. Files with the same beginning date will be deleted")
        parser.add_argument('start', type=str, help="Format YYYY-MM-DD or 'yesterday'")
        parser.add_argument('end', type=str, help="Format YYYY-MM-DD or 'yesterday'")

    def handle(self, *args, **options):
        output_directory = options['output_directory']
        start = options['start']
        end = options['end']

        export(output_directory, start, end)


def delete_files(files):
    for file in files:
        print("Deleting file:", file)
        os.remove(file)


def metdata_export(filepath, first_date, last_date):
    fp = open(filepath, "w")
    csv_writer = csv.DictWriter(fp, ["date_time_start", "date_time_end", "latitude", "longitude", "temperature", "rh", "wind_speed"])
    csv_writer.writeheader()

    date_time = first_date

    interval = 10 # in minutes

    while date_time < last_date:
        initial_time = date_time
        final_time = date_time + datetime.timedelta(minutes=interval)

        # print("Initial: ", initial_time)
        # print("Final: ", final_time)

        query = Q(date_time__gt=initial_time) & Q(date_time__lt=final_time)

        information = MetDataAll.objects.filter(query).aggregate(latitude=Avg('latitude'),
                                                                 longitude=Avg('longitude'),
                                                                 temperature_2t=Avg(F('TA1') + F('TA2')),
                                                                 rh_2t=Avg(F('RH1') + F('RH2')))

        information_wind = MetDataWind.objects.filter(query).aggregate(wind_speed_2t=Avg(F('WSR1') + F('WSR2')))

        if information['latitude'] is None or \
            information['longitude'] is None or \
            information['temperature_2t'] is None:
            date_time += datetime.timedelta(minutes=interval)

            continue

        # print(information)
        information['latitude'] = "{:.4f}".format(information['latitude'])
        information['longitude'] = "{:.4f}".format(information['longitude'])
        information['date_time_start'] = date_time.strftime("%Y-%m-%d %H:%M:%S")
        information['date_time_end'] = final_time.strftime("%Y-%m-%d %H:%M:%S")
        information['wind_speed'] = "{:.2f}".format(information_wind['wind_speed_2t']/2)
        information['temperature'] = "{:.2f}".format(information['temperature_2t']/2)
        information['rh'] = "{:.2f}".format(information['rh_2t'] / 2)

        # print(information)

        del(information['temperature_2t'])
        del(information['rh_2t'])
        csv_writer.writerow(information)

        date_time += datetime.timedelta(minutes=10)

    fp.close()


def export(output_directory, start, end):
    first_date = datetime.datetime.strptime(start, "%Y-%m-%d")

    if end == "yesterday":
        last_date = utils.last_midnight()

    else:
        last_date = datetime.datetime.strptime(end, "%Y-%m-%d")
        last_date = utils.set_utc(last_date)

    first_date = utils.set_utc(first_date)

    first_date_formatted = first_date.strftime("%Y%m%d")
    filename = "metdata_summary_{}_{}.csv".format(first_date_formatted, last_date.strftime("%Y%m%d"))

    file_path = os.path.join(output_directory, filename)

    # It will delete all the files that started the same day for the same metdata type (all, wind)
    files_to_delete = glob.glob(os.path.join(output_directory, "metdata_summary_{}_*.csv").format(first_date_formatted))
    if file_path in files_to_delete:
        files_to_delete.remove(file_path)   # In case that this script is re-generating an existing file

    first_date.replace(minute=10)
    metdata_export(file_path, first_date, last_date)

    delete_files(files_to_delete)
