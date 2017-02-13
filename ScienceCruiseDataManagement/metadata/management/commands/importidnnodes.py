from django.core.management.base import BaseCommand, CommandError
from metadata.models import IdnNode
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Adds data to the idn node table.'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'])

    def import_data_from_csv(self, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                idnnode = IdnNode()
                idnnode.idn_node_short_name = row['IDN_NODE_SHORT_NAME']
                idnnode.idn_node_use_description = row['IDN_NODE_USE_DECRIPTION']
                idnnode.idn_node_long_name = row['IDN_NODE_USE_DECRIPTION']
                idnnode.keyword_version = row['KEYWORD_VERSION']
                idnnode.revision_date = row['REVISION_DATE']
                idnnode.keyword_status = row['KEYWORD_STATUS']
                idnnode.download_date = row['DOWNLOAD_DATE']

                idnnode.save()