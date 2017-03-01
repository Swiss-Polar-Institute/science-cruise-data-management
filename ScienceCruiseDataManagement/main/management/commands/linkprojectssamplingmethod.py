from django.core.management.base import BaseCommand, CommandError
from main.models import Project, SamplingMethod
from django.db.models import Q

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