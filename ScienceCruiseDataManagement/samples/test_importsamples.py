from dateutil.tz import tzfile
from django.test import TransactionTestCase, TestCase

from main.models import Ship, Mission, Leg, Project, Person, Event, ImportedFile, Organisation, Country, Leg, Port,\
    SamplingMethod, Platform, PlatformType

from samples.models import StorageType, Preservation, Sample

from samples.management.commands.importsamples import SampleImporter, InvalidSampleFileException

import datetime
import tempfile
import shutil
import os
import pytz

# python3 manage.py test -v 2 samples.test_importsamples.ImportSamplesTest.test_import_one_row_event_success

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class ImportSamplesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ImportSamplesTest, cls).setUpClass()

        country = Country.objects.create(name="Switzerland")
        organisation = Organisation.objects.create(name="SPI", country=country)
        mission = Mission.objects.create(name="Greenland Circumnavigation Expedition", acronym="GLACE", institution=organisation)

        start_port_country = Country.objects.create(name="Germany")
        start_port = Port.objects.create(name="Kiel", code="KIE", country=start_port_country, latitude=53, longitude=10)

        end_port_country = Country.objects.create(name="Iceland")
        end_port = Port.objects.create(name="Reykjavik", code="REY", country=end_port_country, latitude=65, longitude=-3)

        sampling_method = SamplingMethod.objects.create(name="Getting soil")

        leg = Leg.objects.create(number=1, start_date_time=datetime.datetime(2019, 7, 25, tzinfo=pytz.UTC), start_port=start_port, end_port=end_port,
                                      end_date_time=datetime.datetime(2019, 8, 22, tzinfo=pytz.UTC))
        project = Project.objects.create(number=15, mission=mission)
        project.sampling_methods.add(sampling_method)

        preservation = Preservation.objects.create(name="frozen")

        # self.event = Event.objects.create(sampling_method=self.sampling_method, data=False, samples=True)

        pi = Person.objects.create(name_first="Jen", name_last="Thomas", initials="JT")

        platform_type = PlatformType.objects.create(name="Ship")
        platform = Platform.objects.create(name="AT", uuid="008c5a33-12f7-4027-a531-60baa8073618", platform_type=platform_type)

        ship = Ship.objects.create(shortened_name="AT", name=platform)

    def setUp(self):
        self.temp_directory = tempfile.mkdtemp()
        self.sample_importer = SampleImporter()

    def tearDown(self):
        shutil.rmtree(self.temp_directory)

    def _copy_file_to_tmp_dir(self, file_name):
        # When copying files creates a new one
        self.temp_directory = tempfile.mkdtemp()
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
        file_path = self._copy_file_to_tmp_dir("empty.csv")

        expected_exception_message = "Error in file: {}. Some mandatory fields don't exist: ['contents', 'crate_number', 'destination', 'event_number', 'expedition', 'glace_sample_number', 'julian_day', 'leg_number', 'offloading_port', 'preservation', 'project_number', 'project_pi_initials', 'project_sample_number', 'ship', 'storage_location', 'storage_type']".format(
                                 file_path)

        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory(self.temp_directory)

    def test_import_csv_valid_header(self):
        file_path = self._copy_file_to_tmp_dir("valid_headers.csv")
        self.sample_importer.import_data_from_directory(self.temp_directory)

    def test_import_one_row_no_storage_type(self):
        file_path = self._copy_file_to_tmp_dir("one_row_2263.csv")

        expected_exception_message = "Storage type: {} not available in the database".format("-20 deg freezer")

        self.sample_importer.import_data_from_directory(self.temp_directory)

        self.assertIn(expected_exception_message, self.sample_importer.warning_messages)

    def test_import_invalid_pi(self):
        file_path = self._copy_file_to_tmp_dir("one_row_invalid_pi.csv")

        StorageType.objects.create(name="-20 deg freezer")

        sampling_method = SamplingMethod.objects.get(name="Getting soil")

        Event.objects.create(number=2265, sampling_method=sampling_method, data=False, samples=True)

        self.sample_importer.import_data_from_directory(self.temp_directory)

        # self.assertIn(self.sample_importer.warning_messages, "Cannot insert row: person 'ME' does not exist in the database")
        self.assertIn("Cannot insert row: person 'ME' does not exist in the database", self.sample_importer.warning_messages)

    def test_import_one_row_event_not_finished(self):
        file_path = self._copy_file_to_tmp_dir("one_row_2263.csv")

        StorageType.objects.create(name="-20 deg freezer")

        sampling_method = SamplingMethod.objects.get(name="Getting soil")

        Event.objects.create(number=2263, sampling_method=sampling_method, data=False, samples=True)

        expected_exception_message = "ERROR importing sample: Sample: AT/GLACE/1/15/216/2263/JT/Nut_5m has the event: 2263 with outcome: Not yet happened"
        with self.assertRaisesMessage(InvalidSampleFileException, expected_exception_message):
            self.sample_importer.import_data_from_directory(self.temp_directory)

        self.assertEqual(self.sample_importer.warning_messages, [])

    def test_import_one_row_event_success(self):
        file_path = self._copy_file_to_tmp_dir("one_row_2264.csv")

        StorageType.objects.create(name="-20 deg freezer")

        self.assertEqual(Sample.objects.count(), 0)

        sampling_method = SamplingMethod.objects.get(name="Getting soil")

        Event.objects.create(number=2264, sampling_method=sampling_method, data=False, samples=True, outcome="Success")

        self.sample_importer.import_data_from_directory(self.temp_directory)

        self.assertEqual(Sample.objects.count(), 1)

        sample = Sample.objects.all()[0]

        self.assertEqual(sample.expedition_sample_code, "AT/GLACE/1/15/216/2264/JT/Nut_5m")
        self.assertEqual(sample.event.number, 2264)
        self.assertEqual(sample.storage_type, StorageType.objects.get(name="-20 deg freezer"))
        self.assertEqual(sample.contents, "sterile seawater")
        self.assertEqual(sample.destination, 'Alfred Wegener Institute, Bremerhaven, Germany')
        self.assertEqual(sample.file, "one_row_2264.csv")
        self.assertEqual(sample.julian_day, 216)
        self.assertEqual(sample.leg.number, 1)
        self.assertEqual(sample.mission.acronym, "GLACE")
        self.assertEqual(sample.project_sample_number, "Nut_5m")
        self.assertEqual(sample.crate_number, "67")
        self.assertEqual(sample.storage_location, "hull")
        self.assertEqual(sample.offloading_port, "Bremerhaven, Germany")
        self.assertEqual(sample.comments, "Important")
        self.assertEqual(sample.preservation.name, "frozen")

        self.assertEqual(sample.other_data, {"color": "blue", "collection_temperature": "-4"})

    def test_import_one_row_failure_warning(self):
        file_path = self._copy_file_to_tmp_dir("one_row_2263_no_contents.csv")

        StorageType.objects.create(name="-20 deg freezer")

        self.assertEqual(Sample.objects.count(), 0)

        sampling_method = SamplingMethod.objects.get(name="Getting soil")

        Event.objects.create(number=2264, sampling_method=sampling_method, data=False, samples=True, outcome="Success")

        self.sample_importer.import_data_from_directory(self.temp_directory)

        self.assertEqual(Sample.objects.count(), 0)

        self._assertOneItemContains("Row with empty contents", self.sample_importer.warning_messages)

    def test_code_generated_spreadsheet_not_matching(self):
        file_path = self._copy_file_to_tmp_dir("one_row_code_not_matching.csv")

        StorageType.objects.create(name="-20 deg freezer")

        self.assertEqual(Sample.objects.count(), 0)

        sampling_method = SamplingMethod.objects.get(name="Getting soil")

        Event.objects.create(number=2270, sampling_method=sampling_method, data=False, samples=True, outcome="Success")

        self.sample_importer.import_data_from_directory(self.temp_directory)

        self.assertEqual(Sample.objects.count(), 0)

        self._assertOneItemContains("generated_expedition_sample_code != spreadsheet sample code", self.sample_importer.warning_messages)

    def _assertOneItemContains(self, string, items):
        found = False

        for item in items:
            if string in item:
                found = True

        self.assertTrue(found)
