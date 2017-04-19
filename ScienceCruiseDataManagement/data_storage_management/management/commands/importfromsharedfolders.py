from django.core.management.base import BaseCommand, CommandError
from data_storage_management.models import Directory, DirectoryImportLog
from data_storage_management import cifs_utils

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
    help = 'Copies data from Windows shared folders into ace_data'

    def add_arguments(self, parser):
        parser.add_argument('import', type=str)

    def handle(self, *args, **options):
        shared_resource_directories = Directory.objects.filter(shared_resource__isnull=False).filter(backup_disabled=False).order_by('shared_resource')

        for shared_resource_directory in shared_resource_directories:
            importer = cifs_utils.Importer(shared_resource_directory.shared_resource.ip,
                                           shared_resource_directory.shared_resource.shared_resource,
                                           shared_resource_directory.shared_resource.username,
                                           shared_resource_directory.shared_resource.password,
                                           shared_resource_directory.source_directory,
                                           shared_resource_directory.destination_directory)

            importer.run()
            importer.register_import(shared_resource_directory)