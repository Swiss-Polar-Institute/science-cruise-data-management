from django.core.management.base import BaseCommand, CommandError
from main.models import Project, SamplingMethod
from django.db.models import Q

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
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for project in Project.objects.all().order_by('number'):
            print(project)
            print(project.number)
            sampling_methods_for_this_project = SamplingMethod.objects.filter(
                Q(definition__icontains="project {})".format(project.number)) |
                Q(name__icontains="project {})".format(project.number)) |
                Q(definition__iendswith="project {}".format(project.number)) |
                Q(name__iendswith="project {}".format(project.number))
            )
            for sampling_method in sampling_methods_for_this_project:
                print(sampling_method)

            print("Control+C to Cancel")
            input()

            project.sampling_methods = sampling_methods_for_this_project