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

    if end == "yesterday":
        last_date = utils.last_midnight()
    else:
        last_date = datetime.datetime.strptime(end, "%Y-%m-%d")
        last_date = utils.set_utc(last_date)

    first_date = utils.set_utc(first_date)

    filename = "metdata_{}_{}_{}.csv".format(data_type, first_date.strftime("%Y%m%d"), last_date.strftime("%Y%m%d"))

    file_path = os.path.join(output_directory, filename)

    if data_type == "all":
        table = MetDataAll
    elif data_type == "wind":
        table = MetDataWind
    else:
        assert False

    # It will delete all the files that started the same day for the same metdata type (all, wind)
    files_to_delete = glob.glob(os.path.join(output_directory, "metdata_{}_{}_*.csv"))

    utils.export_table(table, file_path, first_date, last_date)

    delete_files(files_to_delete)
