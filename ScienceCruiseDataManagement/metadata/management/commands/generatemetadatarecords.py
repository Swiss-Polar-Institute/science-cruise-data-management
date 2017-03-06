from django.core.management.base import BaseCommand, CommandError
from metadata.models import MetadataEntry
from metadata.metadataentry_to_dif import MetadataRecordGenerator

class Command(BaseCommand):
    help = 'Generate metadata records'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str)
        parser.add_argument('metadata_id', type=str)

    def handle(self, *args, **options):
        output_directory = options['output_directory']
        record = options['metadata_id']

        if record == "all":
            for metadata_entry in MetadataEntry.objects.all().order_by('entry_id'):
                export_metadata_file = MetadataRecordGenerator(metadata_entry)
                save(output_directory, record, export_metadata_file.do())
        else:
            metadata_entry = MetadataEntry.objects.get(entry_id=record)
            export_metadata_file = MetadataRecordGenerator(metadata_entry)
            save(output_directory, record, export_metadata_file.do())

def save(output_directory, record, data):
    file_path = "{}/metadata-record-{}.xml".format(output_directory, record)
    fp = open(file_path, "wb")
    fp.write(data)
    fp.close()
