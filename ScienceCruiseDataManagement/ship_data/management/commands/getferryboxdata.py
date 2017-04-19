from django.core.management.base import BaseCommand, CommandError
from ship_data.models import Ferrybox
import csv
import glob
import os
import subprocess
import datetime
from main import utils

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
            oxygen = line[12]
            salinity = line[21]
            conductivity = line[22]
            temperature = line[23]
            fluorimeter = line[25]

            date_time = datetime.datetime.strptime("{}{}".format(date, time),
                                                   "%d%m%y%H%M%S")

            date_time = utils.set_utc(date_time)

            ferrybox_information = Ferrybox()
            ferrybox_information.date_time = date_time
            ferrybox_information.salinity = salinity
            ferrybox_information.conductivity = conductivity
            ferrybox_information.oxygen = oxygen
            ferrybox_information.temperature = temperature
            ferrybox_information.fluorimeter = fluorimeter

            ferrybox_information.save()