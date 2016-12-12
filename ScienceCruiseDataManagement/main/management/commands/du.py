from django.core.management.base import BaseCommand, CommandError
from main.models import FilesStorage, FilesStorageGeneral
from django.conf import settings
import subprocess
import os
import shutil

class Command(BaseCommand):
    help = 'Test adding a country'

    @staticmethod
    def du(path):
        """disk usage in human readable format (e.g. '2,1GB')"""
        path = os.path.join(settings.BASE_STORAGE_DIRECTORY, path)
        return subprocess.check_output(['du', '-s', path]).split()[0].decode('utf-8')

    @staticmethod
    def space():
        space = shutil.disk_usage(settings.BASE_STORAGE_DIRECTORY)
        return {'used': space.used/1024, 'free': space.free/1024}

    def add_arguments(self, parser):
        parser.add_argument('update', type=str)

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


    def handle(self, *args, **options):
        self.df_instrumentation()
        self.du_general_storage()
