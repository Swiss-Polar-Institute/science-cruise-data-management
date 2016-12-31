from django.core.management.base import BaseCommand, CommandError
from data_storage_management.models import Directory
from django.conf import settings
import subprocess
import os
import shutil


class Command(BaseCommand):
    help = 'Copies data from staging areas into the ace_data'

    def add_arguments(self, parser):
        parser.add_argument('import', type=str)

    def handle(self, *args, **options):
        importer = Importer()
        importer.run()


class Importer:
    def __init__(self):
        pass

    def run(self):
        nas_directories = os.listdir(settings.NAS_STAGING_MOUNT_POINT)
        all_db_staging_directories = Directory.objects.all().filter(staging_directory__isnull=False)

        for staging_directory in all_db_staging_directories:
            print("From: {} To: {}".format(staging_directory.source))
            nas_directories.remove(staging_directory.source)

            print("rsync {} {}".format(staging_directory.source, staging_directory.destination))

        print("Directories without DB entry")