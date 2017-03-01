from django.core.management.base import BaseCommand, CommandError
from metadata.models import MetadataEntry, Distribution
from django.conf import settings

import os

class Command(BaseCommand):
    help = 'Updates directory usage on the metadata entries.'

    def add_arguments(self, parser):
        parser.add_argument('metadata_id', type=str, help="Can be all for all the metadata")

    def handle(self, *args, **options):
        metadata_id = options['metadata_id']

        if metadata_id == "all":
            metadata_entries = MetadataEntry.objects.all().order_by("entry_id")
        else:
            metadata_entries = MetadataEntry.objects.filter(entry_id=metadata_id)

        for metadata_entry in metadata_entries:
            distribution_size = DistributionSizeUpdater(metadata_entry)
            distribution_size.do()

class DistributionSizeUpdater:
    def __init__(self, metadata_entry):
        self.metadata_entry = metadata_entry

    def do(self):
        files = self._files_for_metadata_entry(self.metadata_entry)
        size = self.calculate_size(files)

        for distribution in Distribution.objects.filter(metadata_entry=self.metadata_entry):
            distribution.distribution_size = size
            distribution.save()

    def calculate_size(self, files):
        size = 0

        for file in files:
            s = os.stat(file)
            size += s.st_size

        return size

    @staticmethod
    def absolute_directory(directory):
        if directory.path_storage is None:
            data_root = "/mnt/ace_data"
        else:
            data_root = directory.path_storage

        if directory.source_directory.endswith("/"):
            return os.path.join(data_root, directory.destination_directory)
        else:
            if directory.source_directory.startswith("/"):
                source = directory.source_directory[1:]
            else:
                source = directory.source_directory
            return os.path.join(data_root, directory.destination_directory, source)

    def _files_for_metadata_entry(self, metadata_entry):
        files = set()

        for directory in metadata_entry.directory.all():
            absolute_path = self.absolute_directory(directory)
            print("Processing: {} (DirectoryID: {})".format(absolute_path,
                                                            directory.id))
            if not os.path.exists(absolute_path):
                print("Path: {} doesn't exist. Aborting".format(absolute_path))
                exit(1)

            for (dirpath, dirnames, filenames) in os.walk(self.absolute_directory(directory)):
                for filename in filenames:
                    absolute_path_file = os.path.join(dirpath, filename)
                    files.add(absolute_path_file)

        return files