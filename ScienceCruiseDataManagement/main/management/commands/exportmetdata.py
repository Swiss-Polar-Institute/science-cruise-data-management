from django.core.management.base import BaseCommand, CommandError
from ship_data.models import MetDataAll, MetDataWind
from main import utils
import os
import shutil
import re

class Command(BaseCommand):
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str)

    def handle(self, *args, **options):
        output_directory = options['output_directory']

        new_files = []
        new_files.append(export("all", output_directory))
        new_files.append(export("wind", output_directory))

        delete_old_files(output_directory, new_files)


def delete_old_files(output_directory, new_files):
    all_files = os.listdir(output_directory)

    files_to_delete = []
    for file in all_files:
        if re.match("^metdata_.+_.+_.+\.csv$", file) and file != "README.txt":
            files_to_delete.append(file)

    for new_file in new_files:
        files_to_delete.remove(new_file)

    for file_to_delete in files_to_delete:
        print("Deleting old file:", file_to_delete)
        os.remove(os.path.join(output_directory, file_to_delete))

def export(data_type, output_directory):
    first_date = MetDataAll.objects.earliest().date_time
    last_date = MetDataAll.objects.latest().date_time

    last_date = utils.last_midnight(last_date)

    filename = "metdata_{}_{}_{}.csv".format(data_type, first_date.strftime("%Y%m%d"), last_date.strftime("%Y%m%d"))

    file_path = os.path.join(output_directory, filename)

    if data_type == "all":
        table = MetDataAll
    elif data_type == "wind":
        table = MetDataWind
    else:
        assert False

    utils.export_table_fast(table, file_path)

    return filename