from django.core.management.base import BaseCommand, CommandError
from ship_data.models import MetDataAll, MetDataWind
from main import utils
import os


class Command(BaseCommand):
    help = 'Outputs the track in CSV format.'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str)

    def handle(self, *args, **options):
        export_all_data(options['output_directory'])
        export_wind_data(options['output_directory'])


def export_all_data(output_directory):
    first_date = MetDataAll.objects.earliest().date_time
    last_date = MetDataAll.objects.latest().date_time

    last_date = utils.last_midnight(last_date)

    filename = "metdata_all_{}_{}.csv".format(first_date.strftime("%Y%m%d"), last_date.strftime("%Y%m%d"))

    file_path = os.path.join(output_directory, filename)

    utils.export_table(MetDataAll, file_path)


def export_wind_data(output_directory):
    # TODO: refactor with previous function
    first_date = MetDataWind.objects.earliest().date_time
    last_date = MetDataWind.objects.latest().date_time

    last_date = utils.last_midnight(last_date)

    filename = "metdata_wind_{}_{}.csv".format(first_date.strftime("%Y%m%d"), last_date.strftime("%Y%m%d"))

    file_path = os.path.join(output_directory, filename)

    utils.export_table(MetDataWind, file_path)
