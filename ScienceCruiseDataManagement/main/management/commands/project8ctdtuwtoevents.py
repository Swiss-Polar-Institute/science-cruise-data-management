from django.core.management.base import BaseCommand, CommandError
from main.models import Project, Sample, EventsConsistencyV2
import re

def get_information_line(string, project_sample_number):
    if string in project_sample_number:
        m = re.match(".*{}([0-9]+).*".format(string), project_sample_number)
        if m is None:
            # print("sample with {} but can't be found: {}".format(string, project_sample_number))
            return None

        return m.group(1)
    else:
        return None

def get_information(project_sample_number):
    ctd = get_information_line("CTD", project_sample_number)
    uw = get_information_line("UW", project_sample_number)

    if ctd is not None and uw is not None:
        print("Project sample number with CTD and UW information?", project_sample_number)
        assert False

    if ctd is not None:
        return ("CTD", ctd)
    elif uw is not None:
        return ("UW", uw)
    else:
        # Some other type of sample
        return ("Other", None)

class Command(BaseCommand):
    help = 'Link project 8 CTD/UW numbers to events'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)
        pass

    def handle(self, *args, **options):
        if options['action'] == "link":
            self.link()
        elif options['action'] == "report":
            self.report()
        else:
            assert False

    def report(self):
        print("TODO report")

    def link(self):
        project = Project.objects.get(number=8)
        samples = Sample.objects.filter(project=project).order_by('julian_day')

        for sample in samples:
            # CTD samples are like: AT/ACE/2/8/025/934/RS/CTD9_0125_5m_CSP_R1
            # Underway samples are like: AT/ACE/2/8/026/951/RS/UW71_0600_0127_flow_citometry_R3

            project_sample_code = sample.project_sample_number
            # print("Project sample number:", project_sample_number)
            (type_of_information, event_from_project_code) = get_information(project_sample_code)

            project_to_event = EventsConsistencyV2()

            if type_of_information == "CTD" or type_of_information == "UW":
                project_to_event.type = type_of_information
                project_to_event.event_from_project_code = event_from_project_code
                project_to_event.event_from_sample = sample.event
                project_to_event.project = sample.project

                project_to_event.save()
