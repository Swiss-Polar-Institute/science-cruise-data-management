from main.management.commands import importsamples

from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Project

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
    help = 'Validates samples that are in the database'

    def add_arguments(self, parser):
        parser.add_argument('--project', type=int, help="Project number to analyse samples from")

    def handle(self, *args, **options):
        validate_samples(options['project'])


def validate_samples(project):
    samples_analyzed = 0
    number_of_valid_samples = 0

    if project is None:
        samples_to_analyse = Sample.objects.all()
    else:
        project = Project.objects.get(number=project)
        samples_to_analyse = Sample.objects.filter(project=project)

    total_number_of_samples = len(samples_to_analyse)

    for sample in samples_to_analyse:
        result = importsamples.validate_sample(sample, abort_if_invalid=False)

        if result[0] == False:
            print(result[1])
        else:
            number_of_valid_samples += 1

        samples_analyzed += 1

        if samples_analyzed % 500 == 0:
            print("Analyzed: {} of {} samples".format(samples_analyzed, total_number_of_samples))
            print("Valid samples: {} ({}%)".format(number_of_valid_samples, (number_of_valid_samples/samples_analyzed)*100))

    print("Total number of samples:", samples_analyzed)
    print("Total number of valid samples:", number_of_valid_samples)
    print("Valid samples: {} ({}%)".format(number_of_valid_samples, (number_of_valid_samples / samples_analyzed) * 100))
