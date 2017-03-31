from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Ship, Mission, Leg, Project, Person, Event, Preservation, ImportedFile
import csv
import glob
import codecs
import os
import datetime
from main import utils
import io


class Command(BaseCommand):
    help = 'Adds data to the sample table'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', type=str)

    def handle(self, *args, **options):
        #print(options['directory_name'])
        self.import_data_from_directory(options['directory_name'])

    def import_data_from_directory(self, directory_name):
        for file in glob.glob(directory_name + "/*.csv"):
            basename = os.path.basename(file)
            if ImportedFile.objects.filter(file_name=basename).filter(object_type="Samples").exists():
                print("File already imported: ", basename)
            else:
                print("PROCESSING FILES: " + directory_name + "/*.csv")
                success = self.import_data_from_csv(file)

                if success:
                    utils.add_imported(file, "Samples")
                else:
                    print(basename, "NOT MOVED because some errors processing it")


    def foreign_key_querysets(self, code_string, mission_acronym_string, leg_string, project_number_string,
                              pi_initials_string, event_number_string, preservation):
        querysets = {}
        querysets['ship'] = Ship.objects.filter(shortened_name=code_string)
        querysets['mission'] = Mission.objects.filter(acronym=mission_acronym_string)
        querysets['leg'] = Leg.objects.filter(number=leg_string)
        querysets['project'] =  Project.objects.filter(number=project_number_string)
        querysets['person'] = Person.objects.filter(initials=pi_initials_string)
        querysets['event'] = Event.objects.filter(number=event_number_string)
        querysets['preservation'] = Preservation.objects.filter(name=preservation)

        return querysets

    def check_foreign_keys(self, row, code_string, mission_acronym_string, leg_string, project_number_string, pi_initials_string, event_number_string, preservation):
        qs = self.foreign_key_querysets(code_string, mission_acronym_string, leg_string, project_number_string,
                                        pi_initials_string, event_number_string, preservation)

        how_many_errors_have_ocurred = 0

        if len(qs['event']) != 1:
            self.report_error(row, qs['event'], 'event', event_number_string)
            how_many_errors_have_ocurred += 1

        if len(qs['ship']) != 1:
            self.report_error(row, qs['ship'], 'ship', code_string)
            how_many_errors_have_ocurred += 1

        if len(qs['mission']) != 1:
            self.report_error(row, qs['mission'], 'mission', mission_acronym_string)
            how_many_errors_have_ocurred += 1

        if len(qs['leg']) != 1:
            self.report_error(row, qs['leg'], 'leg', leg_string)
            how_many_errors_have_ocurred += 1

        if len(qs['project']) != 1:
            self.report_error(row, qs['project'], 'project', project_number_string)
            how_many_errors_have_ocurred += 1

        if len(qs['person']) != 1:
            self.report_error(row, qs['person'], 'person', pi_initials_string)
            how_many_errors_have_ocurred += 1

        if 'preservation' in row and preservation != '' and len(qs['preservation']) != 1:
            self.report_error(row, qs['preservation'], 'preservation', row['preservation'])
            how_many_errors_have_ocurred += 1

        return how_many_errors_have_ocurred == 0

    def remove_spaces_columns(self, row):
        for key in row.keys():
            row[key] = row[key].strip()

    def import_data_from_csv(self, filepath):
        reader = csv.DictReader(io.StringIO(utils.normalised_csv_file(filepath)))
        basename = os.path.basename(filepath)

        rows = 0
        skipped = 0
        inserted = 0
        identical = 0
        replaced = 0
        rows_with_errors = 0

        previous_event_time = None

        for row in reader:
            self.remove_spaces_columns(row)

            print("Processing row from file: ", filepath)
            print("Row:", row)

            if row['contents'] == '':
                print("Row with 'contents' field empty")
                print("Do you want to: \n1: Keep processing the row\n2: Skip this row?")
                print("Type 1 or 2")
                answer = input()

                if answer == "1":
                    # It will continue processing the rows
                    pass
                else:
                    # Skips to the next row
                    rows +=1
                    skipped += 1
                    continue

            original_sample_code = row['ace_sample_number']

            code_string = original_sample_code.split('/')[0]
            mission_acronym_string = original_sample_code.split('/')[1]
            leg_string = original_sample_code.split('/')[2]
            project_number_string = original_sample_code.split('/')[3]
            julian_day = "{0:03d}".format(int(original_sample_code.split('/')[4]))
            event_number_string = original_sample_code.split('/')[5]
            pi_initials_string = original_sample_code.split('/')[6]
            project_id_string = original_sample_code.split('/')[7]

            sample_code_string = "/".join((code_string, mission_acronym_string, leg_string,
                                           project_number_string, julian_day, event_number_string,
                                           pi_initials_string, project_id_string))

            # Julian day can be different otherwise we could have:
            # assert original_sample_code == sample_code_string

            sample = Sample()

            sample.expedition_sample_code = sample_code_string
            sample.project_sample_number = row['project_sample_number']
            sample.contents = row['contents']
            sample.crate_number = row['crate_number']
            sample.storage_type = row['storage_type']
            sample.storage_location = row['storage_location']
            sample.offloading_port = row['offloading_port']
            sample.destination = row['destination']
            sample.comments = row.get('comments', None)

            if 'specific_contents' in row:
                # This is an "optional" column: it was ignored until 0b2d3b83cc38d52
                # now only used if it's there
                sample.specific_contents = row['specific_contents']

            sample.file = basename

            code_string = sample.expedition_sample_code.split('/')[0]
            mission_acronym_string = sample.expedition_sample_code.split('/')[1]
            leg_string = sample.expedition_sample_code.split('/')[2]
            project_number_string = sample.expedition_sample_code.split('/')[3]
            julian_day = "{0:03d}".format(int(sample.expedition_sample_code.split('/')[4]))
            pi_initials_string = sample.expedition_sample_code.split('/')[6]
            event_number_string = sample.expedition_sample_code.split('/')[5]

            if 'preservation' in row:
                preservation = row['preservation']
            else:
                preservation = None

            while not self.check_foreign_keys(row, code_string, mission_acronym_string, leg_string,
                                          project_number_string, pi_initials_string, event_number_string,
                                          preservation) != 0:
                print("Please fix the broken foreign keys and press ENTER. This row will be retested")
                input()

            rows += 1

            qs = self.foreign_key_querysets(code_string, mission_acronym_string, leg_string,
                                            project_number_string, pi_initials_string, event_number_string,
                                            preservation)

            # Here it updates foreign keys only
            event = qs['event'][0]
            ship = qs['ship'][0]
            mission = qs['mission'][0]
            leg = qs['leg'][0]
            project = qs['project'][0]
            pi_initials = qs['person'][0]

            sample.ship = ship
            sample.mission = mission
            sample.leg = leg
            sample.project = project
            sample.julian_day = int(julian_day) # So when we compare is the same as what it comes from the database
            sample.event = event
            sample.pi_initials = pi_initials

            if 'preservation' in row and preservation != '':
                sample.preservation = qs['preservation'][0]

            outcome = self.update_database(sample)
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

        return rows_with_errors == 0

    def report_error(self, row, query_set, object_type, lookup_value):
        """ Shows an error printing the line and an error message. """
        print("error in line:", row)
        if len(query_set) == 0:
            print("Cannot insert row: {} '{}' does not exist in the database".format(object_type, lookup_value))
            # print(format(object_type), ": ", query_set)
        elif len(query_set) > 1:
            print("There are too many {} objects".format(object_type))
            print(format(object_type), ": ", query_set)

    def find_sample(self, key):
        """Find a sample relating to a key"""
        sample_queryset = Sample.objects.filter(expedition_sample_code=key)
        if sample_queryset.exists():
            return sample_queryset[0]
        else:
            return None

    def update_database(self, spreadsheet_sample):
        existing_sample = self.find_sample(spreadsheet_sample.expedition_sample_code)

        if existing_sample is None:
            validate_sample(spreadsheet_sample)
            spreadsheet_sample.save()
            return "inserted"
        else:
            comparison = self.compare_samples(existing_sample, spreadsheet_sample)
            if comparison == True:
                print("Identical row already in database: ", spreadsheet_sample.expedition_sample_code)
                return "identical"
            else:
                print("Sample number already in database but data are different. \nDatabase row: ", existing_sample, "\nRow from spreadsheet: ", spreadsheet_sample.expedition_sample_code)
                print("Do you want to: \n1: Replace the row in the database with the new row? \n2: Skip this row?")
                print("Type 1 or 2")
                answer = input()

                if answer == "1":
                    spreadsheet_sample.pk = existing_sample.pk
                    validate_sample(spreadsheet_sample)
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

    def compare_samples(self, sample1, sample2):
        same_objects = True
        for field in sample1.__dict__.keys():
            if field != '_state' and field != 'id' and field != 'file':
                sample1_normalize = self._normalize(sample1.__dict__[field])
                sample2_normalize = self._normalize(sample2.__dict__[field])
                if sample1_normalize != sample2_normalize:
                    print("Field: {} in database: {}; in spreadsheet: {}".format(field, sample1.__dict__[field], sample2.__dict__[field]))
                    same_objects = False

        return same_objects


def validate_sampling_method(sample):
    event = sample.event
    project = sample.project

    if event.sampling_method in project.sampling_methods.all():
        return (True, None)
    else:
        return (False, "Sample: {} has a sampling method {} not used by the project: {}".format(sample.expedition_sample_code,
                                                                                               event.sampling_method,
                                                                                               project.number))


def validate_event_outcome(sample):
    event = sample.event

    if event.outcome != "Success":
        return (False, "Sample: {} has the event: {} with outcome: {}".format(sample.expedition_sample_code,
                                                                              event.number,
                                                                              event.outcome))
    else:
        return (True, None)

def julian_day_to_date(julian_day):
    # This is adjusted to the ACE 2016 voyage: we started in December and
    # finished in April so Julian days after 300 are considered from the year 2016
    if julian_day > 300:
        initial_date = datetime.datetime(2016, 1, 1)
    else:
        initial_date = datetime.datetime(2017, 1, 1)

    date = initial_date + datetime.timedelta(days=julian_day-1)

    return date

def validate_julian_date_sample(sample):
    julian_day = sample.julian_day
    leg = sample.leg

    sample_date = julian_day_to_date(julian_day)
    sample_date = utils.set_utc(sample_date)

    if leg.start_time.date() > sample_date.date():
        return(False, "Sample: {} has a julian day: {} represents the date: {} that is before the leg starting date: {}".format(
            sample.expedition_sample_code, sample.julian_day, sample_date, leg.start_time))

    if leg.end_time.date() is not None and leg.end_time.date() < sample_date.date():
        return (False, "Sample: {} has a julian day: {} represents the date: {} that is after the leg ending date: {}".format(
            sample.expedition_sample_code, sample.julian_day, sample_date, leg.end_time))

    return (True, None)

def validate_sample(sample, abort_if_invalid=True):
    validators = [validate_sampling_method, validate_event_outcome, validate_julian_date_sample]

    for validator in validators:
        result = validator(sample)

        if result[0] == False and abort_if_invalid:
            print("ERROR importing sample, will abort")
            print(result[1])
            exit(1)

        if result[0] == False and not abort_if_invalid:
            return result

    return (True, "")
