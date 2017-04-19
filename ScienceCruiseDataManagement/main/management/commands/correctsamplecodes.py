from django.core.management.base import BaseCommand, CommandError
from main.models import Sample
import csv

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
    help = 'Correct sample codes'

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str)

    def handle(self, *args, **options):
        filepath = options['filepath']
        reader = csv.DictReader(open(filepath, "r"))

        count = 0

        for row in reader:
            original_expedition_sample_code = row["expedition_sample_code"]
            corrected_expedition_sample_code = row["corrected_expedition_sample_code"]

            if corrected_expedition_sample_code != "":
                sample = Sample.objects.get(expedition_sample_code=original_expedition_sample_code)
                sample.delete()
                count += 1

        print("Count:", count)