from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, Event, Person, Leg, Project, Sample, EventsConsistency, ProjectUnderwayToEvent
import re
from django.db.utils import IntegrityError

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
        # parser.add_argument('action', type=str)
        pass

    def handle(self, *args, **options):
        self.link()

    def link(self):
        project = Project.objects.get(number=8)
        samples = Sample.objects.filter(project=project).order_by('julian_day')

        for sample in samples:
            # CTD samples are like: AT/ACE/2/8/025/934/RS/CTD9_0125_5m_CSP_R1
            # Underway samples are like: AT/ACE/2/8/026/951/RS/UW71_0600_0127_flow_citometry_R3

            project_sample_number = sample.project_sample_number
            # print("Project sample number:", project_sample_number)
            (type_of_information, number) = get_information(project_sample_number)

            project_to_event = EventsConsistency()

            if type_of_information == "CTD" or type_of_information == "UW":
                project_to_event.type = type_of_information
                project_to_event.thing = number
                project_to_event.event_from_sample = sample.event
                project_to_event.project = sample.project

                existing_entries_for_this_sample = EventsConsistency.objects.filter(project=project).\
                                                                             filter(thing=number).\
                                                                             filter(type=type_of_information)

                for entry in existing_entries_for_this_sample:
                    if entry.event_from_sample != sample.event:
                        print("=======================================================================")
                        print("Contradictory information for project CTD/UW number: {}{}".format(type_of_information, number))
                        print("Expedition sample number: {}, project sample number: {}".format(sample.expedition_sample_code, sample.project_sample_number))
                        print("Now it tries to use event {}".format(sample.event))

                        for s in entry.samples.all():
                            print(
                                "This was recorded as Event {}: expedition sample number {}, project sample number: {}".format(
                                    entry.event_from_sample, s.expedition_sample_code, s.project_sample_number))


                project_to_event_query = EventsConsistency.objects.filter(event_from_sample=project_to_event.event_from_sample). \
                                                                    filter(project=project_to_event.project). \
                                                                    filter(type=project_to_event.type). \
                                                                    filter(thing=project_to_event.thing)

                if project_to_event_query.exists():
                    project_to_event = project_to_event_query[0]
                    project_to_event.samples.add(sample)
                    project_to_event.save()
                else:
                    project_to_event.save()
                    if sample not in project_to_event.samples.all():
                        project_to_event.samples.add(sample)
                        project_to_event.save()
