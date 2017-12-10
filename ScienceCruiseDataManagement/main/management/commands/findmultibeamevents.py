from django.core.management.base import BaseCommand, CommandError
import main.utils_gaps
import pandas

class Command(BaseCommand):
    help = 'Find the times of events from multibeam files'

    def add_arguments(self, parser):
        parser.add_argument('destinationfilepath', type=str, help="Directory to be written to")
        parser.add_argument('originfilepath', type=str, help="")

    def handle(self, *args, **options):
        destinationfilepath = options['destinationfilepath']
        originfilepath = options['originfilepath']

        data_for_gaps = read_database_for_data_for_gaps()
        gaps = main.utils_gaps.calculate_gaps(data_for_gaps)
        main.utils_gaps.save_gaps(destinationfilepath, gaps)


def read_database_for_data_for_gaps():
    # TODO

    return data_for_gaps
