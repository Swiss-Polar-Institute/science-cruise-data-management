from django.core.management.base import BaseCommand, CommandError
from data_storage_management.models import Directory, DirectoryImportLog
from data_storage_management import cifs_utils


class Command(BaseCommand):
    help = 'Copies data from Windows shared folders into ace_data'

    def add_arguments(self, parser):
        parser.add_argument('import', type=str)

    def handle(self, *args, **options):
        shared_resource_directories = Directory.objects.all().filter(shared_resource__isnull=False)

        for shared_resource_directory in shared_resource_directories:
            importer = cifs_utils.Importer(shared_resource_directory.shared_resource.ip,
                                           shared_resource_directory.shared_resource.shared_resource,
                                           shared_resource_directory.shared_resource.username,
                                           shared_resource_directory.shared_resource.password,
                                           shared_resource_directory.source_directory,
                                           shared_resource_directory.destination_directory)

            importer.run()
            importer.register_import(shared_resource_directory)