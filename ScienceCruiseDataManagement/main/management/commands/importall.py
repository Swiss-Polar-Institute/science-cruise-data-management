from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os.path


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
        call_command('importprojects', os.path.join(directory, "projects.csv"))
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

