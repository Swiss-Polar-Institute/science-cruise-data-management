from django.test import TransactionTestCase

from main.models import Ship, Mission, Leg, Project, Person, Event, ImportedFile, Organisation, Country, Leg, Port,\
    SamplingMethod, Platform, PlatformType

from samples.management.commands.importsamples import SampleImporter, InvalidSampleFileException
from django.core.exceptions import ObjectDoesNotExist

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


    def test_import_csv_directory_does_not_exist(self):
        sample_importer = SampleImporter()
        errors = self.sample_importer.import_data_from_directory("/tmp/this_does_not_exist1010")

        self.assertEqual(errors, ["Directory expected. /tmp/this_does_not_exist1010 is not a directory. Aborts."])

    def test_import_csv_directory_does_not_contain_csv(self):
        temp_directory = tempfile.mkdtemp()

        errors = self.sample_importer.import_data_from_directory(temp_directory)

        self.assertEqual(errors, ["Directory {} contains no *.csv files. Nothing done.".format(temp_directory)])

        shutil.rmtree(temp_directory)

    def test_import_csv_invalid_header2(self):
        temp_directory = tempfile.mkdtemp()

        my_data_path = os.path.join(THIS_DIR, 'test_files/empty.csv')

        shutil.copy(my_data_path, temp_directory)

        file_imported = os.path.join(temp_directory, "empty.csv")
        expected_exception_message = "Error in file: {}. Some mandatory fields don't exist: ['glace_sample_number', 'contents', 'project_sample_number', 'contents', 'crate_number', 'storage_location', 'storage_type', 'offloading_port', 'destination']".format(
                                 file_imported)

        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory(temp_directory)

        shutil.rmtree(temp_directory)
