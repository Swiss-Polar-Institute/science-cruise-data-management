from main.management.commands import importsamples

from django.core.management.base import BaseCommand, CommandError
from main.models import Sample


class Command(BaseCommand):
    help = 'Validates samples that are in the database'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('validate', type=str)

    def handle(self, *args, **options):
        validate_samples()


def validate_samples():
    samples_analyzed = 0
    number_of_valid_samples = 0
    total_number_of_samples = Sample.objects.all().count()
    for sample in Sample.objects.all():
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
