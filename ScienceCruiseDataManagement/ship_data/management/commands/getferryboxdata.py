from django.core.management.base import BaseCommand, CommandError
from ship_data.models import Ferrybox
import csv
import glob
import os
import subprocess
import datetime
from main import utils

class Command(BaseCommand):
    help = 'Ferrybox data'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)

    def handle(self, *args, **options):
        if options['action'] == 'get':
            self.get_ferrybox_data()

    def get_ferrybox_data(self):
        s = subprocess.Popen(["ssh", "fbuser@192.168.20.6", "bin/show_last_data.sh"], stdout=subprocess.PIPE,
                                                                                      stderr=subprocess.PIPE)

        fb_csv = s.stdout.read()
        fb_csv = fb_csv.decode("utf-8")

        for line in fb_csv.split("\n"):
            if line == "LOG_COPY: end of data":
                break

            line = line.split(",")
            date = line[0][1:]
            time = line[1]
            salinity = line[21]
            conductivity = line[22]
            temperature = line[23]

            date_time = datetime.datetime.strptime("{}{}".format(date, time),
                                                   "%d%m%y%H%M%S")

            date_time = utils.set_utc(date_time)

            ferrybox_information = Ferrybox()
            ferrybox_information.date_time = date_time
            ferrybox_information.salinity = salinity
            ferrybox_information.conductivity = conductivity
            ferrybox_information.temperature = temperature

            ferrybox_information.save()