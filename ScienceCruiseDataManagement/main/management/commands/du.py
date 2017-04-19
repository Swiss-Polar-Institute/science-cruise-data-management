from django.core.management.base import BaseCommand, CommandError
from main.models import FilesStorage, FilesStorageGeneral
from django.conf import settings
import subprocess
import os
import shutil

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
    help = 'Updates the FilesStorage and FilesStorageGeneral tables for stats about storage'

    def add_arguments(self, parser):
        parser.add_argument('update', type=str)

    def handle(self, *args, **options):
        self.df_instrumentation()
        self.du_general_storage()

    @staticmethod
    def du(path):
        """disk usage in human readable format (e.g. '2,1GB')"""
        path = os.path.join(settings.BASE_STORAGE_DIRECTORY, path)
        return subprocess.check_output(['du', '-s', path]).split()[0].decode('utf-8')

    @staticmethod
    def space():
        space = shutil.disk_usage(settings.BASE_STORAGE_DIRECTORY)
        return {'used': space.used/1024, 'free': space.free/1024}

    def df_instrumentation(self):
        for storage in FilesStorage.objects.all():
            print(storage.relative_path)
            print(self.du(storage.relative_path))
            storage.kilobytes=self.du(storage.relative_path)
            storage.save()

    def du_general_storage(self):
        space = self.space()
        general_storage = FilesStorageGeneral()
        general_storage.free = space['free']
        general_storage.used = space['used']

        general_storage.save()
