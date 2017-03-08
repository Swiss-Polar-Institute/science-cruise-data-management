from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, Event, Person, Leg, Project, Sample, ProjectCtdToEvent, ProjectUnderwayToEvent
import re

def get_information_line(string, project_sample_number):
    if string in project_sample_number:
        m = re.match(".*{}([0-9]+).*".format(string), project_sample_number)
        if m is None:
            print("sample with CTD but can't be found:", project_sample_number)
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

            if type_of_information == "CTD" or type_of_information == "UW":
                if type_of_information == "CTD":
                    project_to_event = ProjectCtdToEvent()
                    project_to_event.project_ctd_cast_number = number

                elif type_of_information == "UW":
                    project_to_event = ProjectUnderwayToEvent()
                    project_to_event.project_underway_number = number

                project_to_event.event = sample.event
                project_to_event.project = project

                if type_of_information == "CTD":
                    existing_entries_for_this_project_cast = ProjectCtdToEvent.objects.filter(project_ctd_cast_number=number).filter(project=project)
                elif type_of_information == "UW":
                    existing_entries_for_this_project_cast = ProjectUnderwayToEvent.objects.filter(project_underway_number=number).filter(project=project)

                for entry in existing_entries_for_this_project_cast:
                    if int(entry.event.number) != int(sample.event.number):
                        print("Contradictory information for project CTD/UW number: {}{}".format(type_of_information, number))
                        print("Expedition sample number: {}, project sample number: {}".format(sample.expedition_sample_code, sample.project_sample_number))

                        for s in entry.samples.all():
                            print(
                                "This was recorded as Event {}: expedition sample number {}, project sample number: {}".format(
                                    entry.event, s.expedition_sample_code, s.project_sample_number))

                        # if isinstance(entry, ProjectCtdToEvent):
                        #     print("Previous project sample number: {} Current sample number: {}".format(entry.project_ctd_cast_number, sample.project_sample_number))
                        # elif isinstance(entry, ProjectUnderwayToEvent):
                        #     print("Previous project sample number: {} Current sample number: {}".format(entry.project_underway_number, sample.project_sample_number))

                        #print("Project 2 event: {}".format(project_to_event))
                        continue

                print("=======")
                project_to_event.save()
                project_to_event.samples.add(sample)
                print("From sample: {} {}".format(sample.expedition_sample_code, sample.project_sample_number))
                print("Saved: {}".format(project_to_event))
                print("")
                print("=======")
                project_to_event.save()
