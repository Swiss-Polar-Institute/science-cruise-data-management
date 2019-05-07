from django.test import TransactionTestCase

from main.models import Ship, Mission, Leg, Project, Person, Event, ImportedFile, Organisation, Country, Leg, Port,\
    SamplingMethod, Platform, PlatformType

from samples.management.commands.importsamples import SampleImporter, InvalidSampleFileException

import datetime
import tempfile
import shutil
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class ImportSamplesTest(TransactionTestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Switzerland")
        self.organisation = Organisation.objects.create(name="SPI", country=self.country)
        self.mission = Mission.objects.create(name="GLACE", institution=self.organisation)

        self.start_port_country = Country.objects.create(name="Germany")
        self.start_port = Port.objects.create(name="Kiel", code="KIE", country=self.start_port_country, latitude=53, longitude=10)

        self.end_port_country = Country.objects.create(name="Iceland")
        self.end_port = Port.objects.create(name="Reykjavik", code="REY", country=self.end_port_country, latitude=65, longitude=-3)

        self.leg = Leg.objects.create(number=1, start_date_time=datetime.datetime(2019, 7, 25), start_port=self.start_port, end_port=self.end_port)
        self.project = Project.objects.create(number=1, mission=self.mission)

        self.sampling_method = SamplingMethod.objects.create(name="Getting soil")

        self.event = Event.objects.create(sampling_method=self.sampling_method, data=False, samples=True)

        self.pi = Person.objects.create(name_first="Jen", name_last="Thomas")

        self.platform_type = PlatformType.objects.create(name="Ship")
        self.platform = Platform.objects.create(name="AT", uuid="008c5a33-12f7-4027-a531-60baa8073618", platform_type=self.platform_type)

        self.ship = Ship.objects.create(shortened_name="AT", name=self.platform)

        self.sample_importer = SampleImporter()

        self.temp_directory = tempfile.mkdtemp()

    def copy_file_to_tmp_dir(self, file_name):
        file_path = os.path.join(THIS_DIR, 'test_files', file_name)
        shutil.copy(file_path, self.temp_directory)

        return os.path.join(self.temp_directory, file_name)

    def test_import_csv_directory_does_not_exist(self):
        expected_exception_message = "Directory expected. /tmp/this_does_not_exist1010 is not a directory. Aborts."
        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory("/tmp/this_does_not_exist1010")

    def test_import_csv_directory_does_not_contain_csv(self):
        expected_exception_message = "Directory {} contains no *.csv files. Nothing done.".format(self.temp_directory)
        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory(self.temp_directory)

    def test_import_csv_invalid_header(self):
        file_path = self.copy_file_to_tmp_dir("empty.csv")

        expected_exception_message = "Error in file: {}. Some mandatory fields don't exist: ['glace_sample_number', 'project_sample_number', 'contents', 'crate_number', 'storage_location', 'storage_type', 'offloading_port', 'destination']".format(
                                 file_path)

        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory(self.temp_directory)

    def test_import_csv_valid_header(self):
        file_path = self.copy_file_to_tmp_dir("valid_headers.csv")
        self.sample_importer.import_data_from_directory(self.temp_directory)

    def test_import_one_row_no_storage_type(self):
        file_path = self.copy_file_to_tmp_dir("one_row.csv")

        expected_exception_message = "Storage type: {} not available in the database".format("-20 deg freezer")

        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory(self.temp_directory)

