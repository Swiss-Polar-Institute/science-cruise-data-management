from django.core.management.base import BaseCommand, CommandError

from data_storage_management import cifs_utils
from data_storage_management.models import Directory, NASResource
from django.conf import settings
import os

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
    help = 'Copies data from staging areas into the ace_data'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)

    def handle(self, *args, **options):
        if options['action'] == 'import':
            db_nas_directories = Directory.objects.filter(nas_resource__isnull=False)

            print("Will import the NAS directories. To be processed: {}".format(len(db_nas_directories)))
            for nas_directory in db_nas_directories:
                importer = cifs_utils.Importer(settings.NAS_IP,
                                               nas_directory.nas_resource.shared_resource,
                                               "guest",
                                               None,
                                               nas_directory.source_directory,
                                               nas_directory.destination_directory)

                importer.run()
                importer.register_import(nas_directory)

        elif options['action'] == 'check':
            nas_shares = NASResource.objects.all()

            directories_in_nas = []
            for nas_share in nas_shares:
                mounted = cifs_utils.Importer.mount(settings.NAS_IP, nas_share.shared_resource)
                files_and_dirs = os.listdir(mounted)

                for file_or_dir in files_and_dirs:
                    if os.path.isdir(os.path.join(mounted, file_or_dir)):
                        report_if_directory_no_exist(file_or_dir, nas_share.shared_resource)

                cifs_utils.Importer.umount(mounted)


def report_if_directory_no_exist(directory, shared_resource):
    query_set = Directory.objects.filter(nas_resource__isnull=False, source_directory=directory)
    exists_in_db = query_set.exists()

    if not exists_in_db:
        print("Directory {} from shared resource {} is not in the database".format(directory, shared_resource))
