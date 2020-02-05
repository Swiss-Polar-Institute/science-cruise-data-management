from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, PositionUncertainty, PositionSource
from django.conf import settings

from main import utils


class Command(BaseCommand):
    help = 'Get dates and times of an event'

    def add_arguments(self, parser):
        parser.add_argument('input_filename', help="Filename containing the event numbers", type=str)
        parser.add_argument('output_filename', help="Filename to output the data into", type=str)

    def handle(self, *args, **options):
        print(options)