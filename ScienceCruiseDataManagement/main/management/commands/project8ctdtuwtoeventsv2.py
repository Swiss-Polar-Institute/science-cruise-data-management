from django.core.management.base import BaseCommand, CommandError
from main.models import Project, Sample, EventsConsistencyV2, Event
import re
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

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
        reported = []

        for event_consistency in EventsConsistencyV2.objects.all().order_by('event_from_expedition_code_id'):
            processing = (event_consistency.event_from_expedition_code, event_consistency.event_from_project_code)

            if processing in reported:
                continue

            query_result = EventsConsistencyV2.objects.filter(
                Q(type=event_consistency.type) &
                Q(event_from_project_code=event_consistency.event_from_project_code) &
                ~Q(event_from_expedition_code=event_consistency.event_from_expedition_code))

            if query_result.exists():
                print("======================")
                print("The sample: {} - {} has an inconsistency".format(event_consistency.sample.expedition_sample_code,
                                                                       event_consistency.sample.project_sample_number))
                print("Expedition Event: {} Project code event: {}".format(event_consistency.event_from_expedition_code,
                                                                       event_consistency.event_from_project_code))
                print("Samples with different result:")

                reported.append((event_consistency.event_from_expedition_code, event_consistency.event_from_project_code))

                for inconsistency in query_result:
                    print("Sample: {} - {} (Expedition event: {} project code event: {}".format(inconsistency.sample.expedition_sample_code,
                                                    inconsistency.sample.project_sample_number,
                                                    inconsistency.event_from_expedition_code, inconsistency.event_from_project_code))

    def link(self):
        EventsConsistencyV2.objects.all().delete()
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

                if event_from_project_code is None:
                    print("No event for number: {}".format(event_from_project_code))
                    continue

                try:
                    project_to_event.event_from_project_code = event_from_project_code
                except ObjectDoesNotExist:
                    print("2 No event for number: {}".format(event_from_project_code))
                    continue

                project_to_event.event_from_expedition_code = sample.event
                project_to_event.project = sample.project
                project_to_event.sample = sample

                project_to_event.save()
