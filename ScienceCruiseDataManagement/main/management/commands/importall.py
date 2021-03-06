from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os.path

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
    help = 'Import all the CSVs (see other commands)'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def handle(self, *args, **options):
        directory = options['directory']

        call_command('importcountries', os.path.join(directory, "countries.csv"))
        call_command('importislands', os.path.join(directory, "islands.csv"))
        call_command('importorganisations', os.path.join(directory, "organisations.csv"))
        call_command('importpeople', os.path.join(directory, "participants.csv"))
        call_command('importprojects', os.path.join(directory, "templates.csv"))
        call_command('importplatformtypes', os.path.join(directory, "platform_types.csv"))
        call_command('importplatforms', os.path.join(directory, "platforms.csv"))
        call_command('importships', os.path.join(directory, "ships.csv"))
        call_command('importdevices', directory + "/")
        call_command('importparentdevices', os.path.join(directory, "parent_devices.csv"))
        call_command('importtimeuncertainties', os.path.join(directory, "time_uncertainty.csv"))
        call_command('importpositionuncertainties', os.path.join(directory, "position_uncertainty.csv"))
        call_command('importtimesources', os.path.join(directory, "time_sources.csv"))
        call_command('importpositionsources', os.path.join(directory, "position_sources.csv"))
        call_command('importeventactiondescriptions', os.path.join(directory, "event_action_description.csv"))
        call_command('importports', os.path.join(directory,"ports.csv"))
        call_command('createdjangousers', "--createusers")

