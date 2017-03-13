from django.core.management.base import BaseCommand, CommandError
from main.models import Sample
import csv

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