from django.core.management.base import BaseCommand
from main.models import Sample
import csv

class Command(BaseCommand):
    help = 'Check if an expedition sample code is listed in the database'

    def add_arguments(self, parser):
        parser.add_argument('input_filename', help="Filename containing the expedition sample codes", type=str)
        parser.add_argument('output_filename', help="Filename to output the missing expedition sample codes into", type=str)


    def handle(self, *args, **options):
        process_input_file(options['input_filename'], options['output_filename'])


def process_input_file(input_filename, output_filename):
    with open(input_filename, 'r') as data_file:
        contents = csv.reader(data_file)
        next(contents, None)  # skip header line

        with open(output_filename, 'w') as output_file:
            writer = csv.writer(output_file)

            header = ['expedition_sample_code']
            writer.writerow(header)

            count_samples_to_check = 0
            count_samples_missing = 0

            for line in contents:
                expedition_sample_code_to_check = line[0]
                count_samples_to_check += 1
                #print(expedition_sample_code_to_check)

                if not Sample.objects.filter(expedition_sample_code=expedition_sample_code_to_check).exists():
                    print("Sample not listed in database:", expedition_sample_code_to_check)
                    writer.writerow([expedition_sample_code_to_check])
                    count_samples_missing += 1

            print("Total samples checked: ", count_samples_to_check)
            print("Number of samples not listed in database: ", count_samples_missing)