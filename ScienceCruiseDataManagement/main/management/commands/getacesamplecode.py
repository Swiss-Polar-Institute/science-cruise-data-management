from django.core.management.base import BaseCommand
from main.models import Sample
import csv


class Command(BaseCommand):
    help = 'Get ACE sample code where a project sample code is provided'

    def add_arguments(self, parser):
        parser.add_argument('input_filename', help="Filename containing the project sample codes", type=str)
        parser.add_argument('output_filename', help="Filename to output the data into", type=str)

    def handle(self, *args, **options):
        process_input_file(options['input_filename'], options['output_filename'])

def process_input_file(input_filename, output_filename):
    with open(input_filename, 'r') as data_file:
        contents = csv.reader(data_file)

        with open(output_filename, 'w') as output_file:
            writer = csv.writer(output_file)

            header = ['project_sample_code', 'ace_sample_code']
            writer.writerow(header)

            for line in contents:
                # read in the project sample code
                project_sample_code = line[0]
                print(project_sample_code)
