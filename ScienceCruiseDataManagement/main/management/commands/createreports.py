from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Project, EventAction, SamplingMethod, SpecificDevice
from data_storage_management.models import Directory
import csv
import os
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'List samples with the events, positions and times'

    def add_arguments(self, parser):
        parser.add_argument('output_directory', type=str)

    def handle(self, *args, **options):
        output_directory = options['output_directory']

        reportProject = ReportProject(output_directory)
        reportProject.do()

        reportSampleWithEvents = ReportSampleWithEvents()
        reportSampleWithEvents.do(output_directory)

class ReportProject():
    def __init__(self, output_directory):
        self._output_directory = output_directory
        os.makedirs("{}/for_data_team".format(output_directory), exist_ok=True)

    def do(self):
        for project in Project.objects.all().order_by('number'):
            self.list_sampling_methods(project)

        self.unasigned_sampling_methods()
        self.devices_without_directories()
        self.sampling_methods_without_directories()
        self.directories_not_linked()

    @staticmethod
    def save_into_file(filepath, header, data):
        print("Saving in", filepath)
        f = open(filepath, "w")
        csv_writer = csv.DictWriter(f, header)
        csv_writer.writeheader()

        csv_writer.writerows(data)

        f.close()

    def list_sampling_methods(self, project):
        filename = "{}/project-{}-sampling-methods.csv".format(self._output_directory, str(project.number).zfill(2))

        information = []
        for sampling_method in project.sampling_methods.all().order_by('id'):
            information.append({'id': sampling_method.id,
                                'name': sampling_method.name})

        ReportProject.save_into_file(filename, ["id", "name"], information)

    def unasigned_sampling_methods(self):
        filename = "{}/for_data_team/unasigned-sampling-method.csv".format(self._output_directory)

        information = []
        for sampling_method in SamplingMethod.objects.all().order_by('id'):
            linked_to_project = sampling_method.project_set.exists()

            if not linked_to_project:
                information.append({'id': sampling_method.id,
                                    'name': sampling_method.name})

        ReportProject.save_into_file(filename, ["id", "name"], information)

    def sampling_methods_without_directories(self):
        filename = "{}/for_data_team/sampling-methods-without-directories.csv".format(self._output_directory)

        information = []

        for sampling_method in SamplingMethod.objects.all().exclude(validity='redundant').order_by('name'):
            linked_to_directory = sampling_method.directory.exists()

            if not linked_to_directory:
                information.append({'id': sampling_method.id,
                                    'sampling_method': str(sampling_method)})

        ReportProject.save_into_file(filename, ["id", "sampling_method"], information)

    def directories_not_linked(self):
        filename = "{}/for_data_team/directories-not-linnked-specific-device-or-sampling-method.csv".format(self._output_directory)

        information = []

        for directory in Directory.objects.all().order_by('id'):
            linked_to_specific_device = SpecificDevice.objects.filter(directory=directory).exists()
            linked_to_sampling_method = SamplingMethod.objects.filter(directory=directory).exists()

            if linked_to_sampling_method==False and linked_to_specific_device==False:
                information.append({'id': directory.id,
                                    'directory': str(directory)})

        ReportProject.save_into_file(filename, ["id", "directory"], information)

    def devices_without_directories(self):
        filename = "{}/for_data_team/specific-devices-without-directories.csv".format(self._output_directory)

        information = []

        for specific_device in SpecificDevice.objects.all().order_by('id'):
            linked_to_directory = specific_device.directory.exists()

            if not linked_to_directory:
                information.append({'id': specific_device.id,
                                    'specific_device': str(specific_device)})

        ReportProject.save_into_file(filename, ["id", "specific_device"], information)


    def list_devices(self, output_directory, project):
        # Not possible yet
        pass


class ReportSampleWithEvents():
    def do(self, output_directory):
        for project in Project.objects.all().order_by('number'):
            self.list_project(output_directory, project)

    def event_action(self, type, event_number):
        start = EventAction.objects.filter(event__number=event_number).filter(type=type)

        if not start.exists():
            start = EventAction.objects.filter(event__number=event_number).filter(type=EventAction.tinstant())

        assert len(start) == 1 or len(start) == 0
        if len(start) == 1:
            return start[0]
        else:
            return None

    def information(self, event_action):
        if event_action is None:
            date_time = latitude = longitude = ""
            return date_time, latitude, longitude

        if event_action.time is not None:
            date_time = event_action.time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_time = ""

        latitude = event_action.latitude
        longitude = event_action.longitude

        return date_time, latitude, longitude

    def event_start_action(self, event_number):
        return self.event_action(EventAction.tbegin(), event_number)

    def event_stop_action(self, event_number):
        return self.event_action(EventAction.tends(), event_number)

    def list_project(self, output_directory, project):
        samples = Sample.objects.filter(project=project).order_by('julian_day')
        filename = "{}/project-{}-samples-report.csv".format(output_directory, str(project.number).zfill(2))
        temporary_filename = filename + ".tmp"

        print("Saving in {}".format(temporary_filename))

        f = open(temporary_filename, "w")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["ace_sample_number", "project_sample_number", "station_number", "event_number", "sampling_method",
                            "start_time (UTC)", "start_latitude", "start_longitude",
                            "end_time (UTC)", "end_latitude", "end_longitude",
                            "event_comments", "contents", "specific_contents",
                            "offloading_port", "destination"])

        for sample in samples:
            ace_sample_number = sample.expedition_sample_code
            project_sample_number = sample.project_sample_number
            event_number = sample.event_id
            contents = sample.contents
            specific_contents = sample.specific_contents
            sampling_method = sample.event.sampling_method
            event_start_action = self.event_start_action(sample.event.number)
            event_end_action = self.event_stop_action(sample.event.number)
            event_comments = sample.event.comments
            offloading_port = sample.offloading_port
            destination = sample.destination

            (start_time, start_latitude, start_longitude) = self.information(event_start_action)
            (end_time, end_latitude, end_longitude) = self.information(event_end_action)

            if sample.event.station is not None:
                station_number = sample.event.station.name
            else:
                station_number = ""
            #
            #     if sample.event.station.arrival_time is not None:
            #         date_time = sample.event.station.arrival_time.strftime("%Y-%m-%d %H:%M:%S")
            #     else:
            #         date_time = ""
            # else:
            #     latitude = longitude = date_time = station_number = ""

            csv_writer.writerow([ace_sample_number, project_sample_number, station_number, event_number, sampling_method,
                                 start_time, start_latitude, start_longitude,
                                 end_time, end_latitude, end_longitude,
                                 event_comments, contents, specific_contents,
                                 offloading_port, destination])

        f.close()
        os.replace(temporary_filename, filename)
