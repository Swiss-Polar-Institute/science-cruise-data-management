from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from main.models import Ship, Mission, Leg, Project, Person, Event, ImportedFile, Organisation, Country, Leg, Port,\
    SamplingMethod, Platform, PlatformType
from samples.models import Sample, Preservation, StorageType
import colorama
import csv
import sys
import glob
import os
import datetime
from main import utils
import io
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


class Command(BaseCommand):
    help = 'Adds data to the sample table'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', type=str)

    def handle(self, *args, **options):
        sample_importer = SampleImporter()

        try:
            sample_importer.import_data_from_directory(options['directory_name'])
        except InvalidSampleFileException as e:
            print_error(e.message)

        print_error("ATTENTION: SAMPLES NOT IMPORTED!")

        for warning in sample_importer.warning_messages:
            print_error(warning)


class InvalidSampleFileException(RuntimeError):
   def __init__(self, message):
      self.message = message


class SpreadsheetRow(object):
    _mandatory_headers = ["contents", "ship", "expedition", "leg_number", "project_number", "julian_day",
                          "event_number", "project_pi_initials", "project_sample_number", "storage_location",
                          "offloading_port", "destination", "glace_sample_number", "crate_number", "storage_type",
                          "preservation"]

    _optional_headers = ["comments", "specific_contents"]

    def __init__(self, row):
        self._row = row
        self._remove_spaces_expedition_columns(row)


    def __str__(self):
        return str(self._row)

    @classmethod
    def verify_header(cls, fieldnames, file_path):
        """ Raise an exception if a mandatory header is missing. """

        mandatory_fields = SpreadsheetRow._mandatory_headers[:]

        if fieldnames is None:
            fieldnames = []

        for field in fieldnames:
            if field in mandatory_fields:
                mandatory_fields.remove(field)

        if len(mandatory_fields) > 0:
            mandatory_fields.sort()
            raise InvalidSampleFileException("Error in file: {}. Some mandatory fields don't exist: {}".format(file_path, mandatory_fields))

    def _remove_spaces_expedition_columns(self, row):
        for key in self._mandatory_headers:
            row[key] = row[key].strip()

        for key in self._optional_headers:
            if key in row and row[key] is not None:
                row[key] = row[key].strip()


    @classmethod
    def _header_for_field(cls, field):
        # Makes sure to list all the used headers - this is
        # important for the "other_data"

        assert ((field in cls._mandatory_headers) or (field in cls._optional_headers))
        return field

    def contents(self):
        return self._row[self._header_for_field("contents")]

    def ship(self):
        return self._row[self._header_for_field("ship")]

    def expedition(self):
        return self._row[self._header_for_field("expedition")]

    def leg(self):
        return self._row[self._header_for_field("leg_number")]

    def project_number(self):
        return self._row[self._header_for_field("project_number")]

    def julian_day(self):
        return self._row[self._header_for_field("julian_day")]

    def event_number(self):
        return self._row[self._header_for_field("event_number")]

    def project_pi_initials(self):
        return self._row[self._header_for_field("project_pi_initials")]

    def project_sample_number(self):
        return self._row[self._header_for_field("project_sample_number")]

    def storage_location(self):
        return self._row[self._header_for_field("storage_location")]

    def offloading_port(self):
        return self._row[self._header_for_field("offloading_port")]

    def destination(self):
        return self._row[self._header_for_field("destination")]

    def comments(self):
        return self._row.get(self._header_for_field("comments"), None)

    def glace_sample_number(self):
        return self._row.get(self._header_for_field("glace_sample_number"))

    def crate_number(self):
        return self._row.get(self._header_for_field("crate_number"))

    def storage_type(self):
        return self._row.get(self._header_for_field("storage_type"))

    def specific_contents(self):
        return self._row.get(self._header_for_field("specific_contents"), None)

    def preservation(self):
        return self._row.get(self._header_for_field("preservation"))

    def other_data(self):
        data = {}
        for header in self._row.keys():
            if header not in self._mandatory_headers and header not in self._optional_headers:
                data[header] = self._row[header]

        return data


class SampleImporter(object):
    def __init__(self):
        self.warning_messages = []
        pass

    @transaction.atomic
    def import_data_from_directory(self, directory_name):
        if not os.path.isdir(directory_name):
            raise InvalidSampleFileException("Directory expected. {} is not a directory. Aborts.".format(directory_name))

        file_paths = glob.glob(directory_name + "/*.csv")
        if len(file_paths) == 0:
            raise InvalidSampleFileException("Directory {} contains no *.csv files. Nothing done.".format(directory_name))

        for file in file_paths:
            basename = os.path.basename(file)
            if ImportedFile.objects.filter(file_name=basename).exists():
            # if ImportedFile.objects.filter(file_name=basename).filter(object_type="Samples").exists():
                self.warning_messages.append("File already imported: {}. Skipping this file.".format(basename))
            else:
                print("PROCESSING FILE: " + file)

                success = self._import_data_from_csv(file)

                if success:
                    utils.add_imported(file, "Samples")
                else:
                    self.warning_messages.append("{} NOT MOVED because some errors processing it".format(basename))

        if len(self.warning_messages) != 0:
            # Cancel everything!
            transaction.set_rollback(True)


    def _foreign_key_querysets(self, code_string, mission_acronym_string, leg_string, project_number_string,
                               pi_initials_string, event_number_string, preservation):
        querysets = {}
        querysets['ship'] = Ship.objects.filter(shortened_name=code_string)
        querysets['mission'] = Mission.objects.filter(acronym=mission_acronym_string)
        querysets['leg'] = Leg.objects.filter(number=leg_string)
        querysets['project'] = Project.objects.filter(number=project_number_string)
        querysets['person'] = Person.objects.filter(initials=pi_initials_string)
        querysets['event'] = Event.objects.filter(number=event_number_string)
        querysets['preservation'] = Preservation.objects.filter(name=preservation)

        return querysets

    def _check_foreign_keys(self, row, code_string, mission_acronym_string, leg_string, project_number_string, pi_initials_string, event_number_string, preservation):
        qs = self._foreign_key_querysets(code_string, mission_acronym_string, leg_string, project_number_string,
                                         pi_initials_string, event_number_string, preservation)

        how_many_errors_have_occurred = 0

        if len(qs['event']) != 1:
            self._report_error(row, qs['event'], 'event', event_number_string)
            how_many_errors_have_occurred += 1

        if len(qs['ship']) != 1:
            self._report_error(row, qs['ship'], 'ship', code_string)
            how_many_errors_have_occurred += 1

        if len(qs['mission']) != 1:
            self._report_error(row, qs['mission'], 'mission', mission_acronym_string)
            how_many_errors_have_occurred += 1

        if len(qs['leg']) != 1:
            self._report_error(row, qs['leg'], 'leg', leg_string)
            how_many_errors_have_occurred += 1

        if len(qs['project']) != 1:
            self._report_error(row, qs['project'], 'project', project_number_string)
            how_many_errors_have_occurred += 1

        if len(qs['person']) != 1:
            self._report_error(row, qs['person'], 'person', pi_initials_string)
            how_many_errors_have_occurred += 1

        if len(qs['preservation']) != 1:
            self._report_error(row, qs['preservation'], 'preservation', row['preservation'])
            how_many_errors_have_occurred += 1

        return how_many_errors_have_occurred == 0

    def _row_dictionary_to_model(self, row):
        pass

    def _import_data_from_csv(self, filepath):
        reader = csv.DictReader(io.StringIO(utils.normalised_csv_file(filepath)))
        basename = os.path.basename(filepath)

        rows = 0
        skipped = 0
        inserted = 0
        identical = 0
        replaced = 0
        rows_with_errors = 0

        SpreadsheetRow.verify_header(reader.fieldnames, filepath)

        line_number = 1  # header

        for row in reader:
            line_number += 1

            spreadsheet_row = SpreadsheetRow(row)

            if spreadsheet_row.contents() == "":
                self.warning_messages.append("Row with empty contents: {}".format(spreadsheet_row))

            original_sample_code = spreadsheet_row.glace_sample_number()

            expected_slashes = 7
            actual_slashes = original_sample_code.count("/")
            if actual_slashes != expected_slashes:
                self.warning_messages.append("File: {} Line number: {} original sample code: '{}' not having expected '/'. Actual: {} Expected: {}. Aborting".format(filepath, line_number, original_sample_code, actual_slashes, expected_slashes))
                continue

            code_string = spreadsheet_row.ship()
            mission_acronym_string = spreadsheet_row.expedition()
            leg_string = spreadsheet_row.leg()
            project_number_string = spreadsheet_row.project_number()

            julian_day_string = spreadsheet_row.julian_day()
            try:
                julian_day_formatted = "{0:03d}".format(int(julian_day_string))
            except ValueError:
                self.warning_messages.append("Error: file {} Line number: {} julian day invalid: ".format(filepath, line_number, julian_day_string))
                continue

            event_number_string = spreadsheet_row.event_number()

            pi_initials_string = spreadsheet_row.project_pi_initials()
            project_id_string = spreadsheet_row.project_sample_number()

            generated_expedition_sample_code = "/".join((code_string, mission_acronym_string, leg_string,
                                           project_number_string, julian_day_formatted, event_number_string,
                                           pi_initials_string, project_id_string))

            if generated_expedition_sample_code != spreadsheet_row.glace_sample_number():
                self.warning_messages.append("Error: file {} Line number: {} generated_expedition_sample_code != spreadsheet sample code: {} != {}".format(filepath, line_number, generated_expedition_sample_code, spreadsheet_row.glace_sample_number()))
                continue

            sample = Sample()

            sample.expedition_sample_code = generated_expedition_sample_code
            sample.project_sample_number = spreadsheet_row.project_sample_number()
            sample.contents = spreadsheet_row.contents()
            sample.crate_number = spreadsheet_row.crate_number()
            sample.storage_location = spreadsheet_row.storage_location()

            try:
                storage_type = StorageType.objects.get(name=spreadsheet_row.storage_type())
            except ObjectDoesNotExist:
                self.warning_messages.append("Storage type: {} not available in the database".format(spreadsheet_row.storage_type()))
                continue

            sample.storage_type = storage_type
            sample.offloading_port = spreadsheet_row.offloading_port()
            sample.destination = spreadsheet_row.destination()
            sample.comments = spreadsheet_row.comments()

            sample.specific_contents = spreadsheet_row.specific_contents()

            sample.file = basename

            preservation = spreadsheet_row.preservation()

            if not self._check_foreign_keys(spreadsheet_row, code_string, mission_acronym_string, leg_string,
                                            project_number_string, pi_initials_string, event_number_string,
                                            preservation) != 0:
                self.warning_messages.append("Problems with foreign keys in row")
                continue

            rows += 1

            qs = self._foreign_key_querysets(code_string, mission_acronym_string, leg_string,
                                             project_number_string, pi_initials_string, event_number_string,
                                             preservation)

            # Here it updates foreign keys only
            event = qs['event'][0]
            ship = qs['ship'][0]
            mission = qs['mission'][0]
            leg = qs['leg'][0]
            project = qs['project'][0]
            pi_initials = qs['person'][0]
            sample.preservation = qs['preservation'][0]

            # Updates the rest
            sample.ship = ship
            sample.mission = mission
            sample.leg = leg
            sample.project = project
            sample.julian_day = int(julian_day_string)  # So when we compare is the same as what it comes from the database
            sample.event = event
            sample.pi = pi_initials

            sample.other_data = spreadsheet_row.other_data()

            outcome = self._update_database(sample)
            if outcome == "skipped":
                skipped += 1
            elif outcome == "inserted":
                inserted += 1
            elif outcome == "replaced":
                replaced += 1
            elif outcome == "identical":
                identical += 1
            else:
                print("Something else:", outcome)

        print("TOTAL ROWS PROCESSED= ", rows, "; Inserted = ", inserted, "; Identical = ", identical, "; Skipped = ", skipped, "; Replaced = ", replaced)

        if rows == 0:
            InvalidSampleFileException("Error: no rows found in the file: {}".format(filepath))

        return rows_with_errors == 0 and rows > 0

    def _report_error(self, row, query_set, object_type, lookup_value):
        """ Shows an error printing the line and an error message. """
        if len(query_set) == 0:
            self.warning_messages.append("Cannot insert row: {} '{}' does not exist in the database".format(object_type, lookup_value))
            # print(format(object_type), ": ", query_set)
        elif len(query_set) > 1:
            self.warning_messages.append("There are too many {} objects".format(object_type))
            # print("There are too many {} objects".format(object_type))
            # print(format(object_type), ": ", query_set)

    @staticmethod
    def _find_sample(key):
        """Find a sample relating to a key"""
        sample_queryset = Sample.objects.filter(expedition_sample_code=key)
        if sample_queryset.exists():
            return sample_queryset[0]
        else:
            return None

    def _update_database(self, spreadsheet_sample):
        existing_sample = self._find_sample(spreadsheet_sample.expedition_sample_code)

        if existing_sample is None:
            self.validate_sample(spreadsheet_sample)
            spreadsheet_sample.save()
            return "inserted"
        else:
            comparison = self._compare_samples(existing_sample, spreadsheet_sample)
            if comparison is True:
                print("Identical row already in database: ", spreadsheet_sample.expedition_sample_code)
                return "identical"
            else:
                print("Sample number already in database but data are different. \nDatabase row: ", existing_sample, "\nRow from spreadsheet: ", spreadsheet_sample.expedition_sample_code)
                print("Do you want to: \n1: Replace the row in the database with the new row? \n2: Skip this row?")
                print("Type 1 or 2")
                answer = input()

                if answer == "1":
                    spreadsheet_sample.pk = existing_sample.pk
                    self.validate_sample(spreadsheet_sample)
                    spreadsheet_sample.save()

                    print("Row replaced")
                    return "replaced"
                else:
                    return "skipped"

    def _normalize(self, value):
        if value is None:
            return ""
        else:
            return value

    def _compare_samples(self, sample1, sample2):
        same_objects = True
        for field in sample1.__dict__.keys():
            if field != '_state' and field != 'id' and field != 'file':
                sample1_normalize = self._normalize(sample1.__dict__[field])
                sample2_normalize = self._normalize(sample2.__dict__[field])
                if sample1_normalize != sample2_normalize:
                    print("Field: {} in database: {}; in spreadsheet: {}".format(field, sample1.__dict__[field], sample2.__dict__[field]))
                    same_objects = False

        return same_objects


    def validate_sampling_method(self, sample):
        event = sample.event
        project = sample.project

        if event.sampling_method in project.sampling_methods.all():
            return (True, None)
        else:
            return (False, "Sample: {} has a sampling method {} not used by the project: {}".format(sample.expedition_sample_code,
                                                                                                   event.sampling_method,
                                                                                                   project.number))


    def validate_event_outcome(self, sample):
        event = sample.event

        if event.outcome != "Success":
            return (False, "Sample: {} has the event: {} with outcome: {}".format(sample.expedition_sample_code,
                                                                                  event.number,
                                                                                  event.outcome))
        else:
            return (True, None)


    def julian_day_to_date(self, julian_day):
        initial_date = datetime.datetime(2019, 1, 1)
        date = initial_date + datetime.timedelta(days=julian_day-1)

        return date


    def validate_julian_date_sample(self, sample):
        julian_day = sample.julian_day
        leg = sample.leg

        sample_date = self.julian_day_to_date(julian_day)
        sample_date = utils.set_utc(sample_date)

        if leg.start_date_time.date() > sample_date.date():
            return(False, "Sample: {} has a julian day: {} represents the date: {} that is before the leg starting date: {}".format(
                sample.expedition_sample_code, sample.julian_day, sample_date, leg.start_time))

        if leg.end_date_time.date() is not None and leg.end_date_time.date() < sample_date.date():
            return (False, "Sample: {} has a julian day: {} represents the date: {} that is after the leg ending date: {}".format(
                sample.expedition_sample_code, sample.julian_day, sample_date, leg.end_date_time))

        return (True, None)


    def validate_sample(self, sample, abort_if_invalid=True):
        validators = [self.validate_sampling_method, self.validate_event_outcome, self.validate_julian_date_sample]

        for validator in validators:
            result = validator(sample)

            if result[0] == False and abort_if_invalid:
                raise InvalidSampleFileException("ERROR importing sample: {}".format(result[1]))

            if result[0] == False and not abort_if_invalid:
                return result

        return (True, "")


def print_error(log):
    colorama.init()
    print(colorama.Fore.RED + colorama.Style.BRIGHT + log, end="")
    print(colorama.Style.RESET_ALL)
