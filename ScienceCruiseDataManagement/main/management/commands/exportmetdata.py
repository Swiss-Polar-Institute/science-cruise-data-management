from django.core.management.base import BaseCommand, CommandError
from ship_data.models import MetDataAll, MetDataWind
from main import utils
import os
import shutil
import re
import datetime
import glob

class Command(BaseCommand):
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str, help="Output directory. Files with the same beginning date will be deleted")
        parser.add_argument('start', type=str, help="Format YYYY-MM-DD or 'yesterday'")
        parser.add_argument('end', type=str, help="Format YYYY-MM-DD or 'yesterday'")

    def handle(self, *args, **options):
        output_directory = options['output_directory']
        start = options['start']
        end = options['end']

        export("all", output_directory, start, end)
        export("wind", output_directory, start, end)


def delete_files(files):
    for file in files:
        print("Deleting file:", file)
        os.remove(file)


def export(data_type, output_directory, start, end):
    first_date = datetime.datetime.strptime(start, "%Y-%m-%d")

    if data_type == "all":
        table = MetDataAll
    elif data_type == "wind":
        table = MetDataWind
    else:
        assert False

    if end == "yesterday":
        yesterday = utils.last_midnight()
        last_available_date = table.objects.latest().date_time

        last_date = min(yesterday, last_available_date)

    else:
        last_date = datetime.datetime.strptime(end, "%Y-%m-%d")
        last_date = utils.set_utc(last_date)

    first_date = utils.set_utc(first_date)

    first_date_formatted = first_date.strftime("%Y%m%d")
    filename = "metdata_{}_{}_{}.csv".format(data_type, first_date_formatted, last_date.strftime("%Y%m%d"))

    file_path = os.path.join(output_directory, filename)

    # It will delete all the files that started the same day for the same metdata type (all, wind)
    files_to_delete = glob.glob(os.path.join(output_directory, "metdata_{}_{}_*.csv").format(data_type, first_date_formatted))
    if file_path in files_to_delete:
        files_to_delete.remove(file_path)   # In case that this script is re-generating an existing file

    utils.export_table(table, file_path, first_date, last_date)

    delete_files(files_to_delete)
