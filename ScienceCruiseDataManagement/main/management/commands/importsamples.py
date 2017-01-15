from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Ship, Mission, Leg, Project, Person, Event, Preservation, ImportedFile
import csv
import glob
import codecs
import os
import datetime
from main import utils


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
                print ("File already imported: ", basename)
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

        if preservation != '' and len(qs['preservation']) != 1:
            self.report_error(row, qs['preservation'], 'preservation', row['preservation'])
            how_many_errors_have_ocurred += 1

        return how_many_errors_have_ocurred == 0

    def import_data_from_csv(self, filepath):
        with codecs.open(filepath, encoding = 'utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            basename = os.path.basename(filepath)

            rows = 0
            skipped = 0
            inserted = 0
            identical = 0
            replaced = 0
            rows_with_errors = 0

            for row in reader:
                print("Processing row from file: ", filepath)
                print("Row:", row)
                sample = Sample()
                sample.expedition_sample_code = row['ace_sample_number']
                sample.project_sample_number = row['project_sample_number']
                sample.contents = row['contents']
                sample.crate_number = row['crate_number']
                sample.storage_type = row['storage_type']
                sample.storage_location = row['storage_location']
                sample.offloading_port = row['offloading_port']
                sample.destination = row['destination']
                sample.file = basename

                code_string = sample.expedition_sample_code.split('/')[0]
                mission_acronym_string = sample.expedition_sample_code.split('/')[1]
                leg_string = sample.expedition_sample_code.split('/')[2]
                project_number_string = sample.expedition_sample_code.split('/')[3]
                julian_day = int(sample.expedition_sample_code.split('/')[4])
                pi_initials_string = sample.expedition_sample_code.split('/')[6]
                event_number_string = int(sample.expedition_sample_code.split('/')[5])
                preservation = row['preservation']

                while not self.check_foreign_keys(row, code_string, mission_acronym_string, leg_string,
                                              project_number_string, pi_initials_string, event_number_string,
                                              preservation) != 0:
                    print("Please fix the broken foreign keys and press ENTER. This row will be retested")
                    input()

                rows += 1

                qs = self.foreign_key_querysets(code_string, mission_acronym_string, leg_string,
                                                project_number_string, pi_initials_string, event_number_string,
                                                preservation)

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
                sample.julian_day = julian_day
                sample.event = event
                sample.pi_initials = pi_initials

                if preservation != '':
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

            print("TOTAL ROWS PROCESSED= ",rows, "; Inserted = ", inserted, "; Identical = ", identical, "; Skipped = ", skipped, "; Replaced = ", replaced)

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
                    spreadsheet_sample.save()

                    print("Row replaced")
                    return "replaced"
                else:
                    return "skipped"

    def compare_samples(self, sample1, sample2):
        same_objects = True
        for field in sample1.__dict__.keys():
            if field != '_state' and field != 'id' and field != 'file':
                if sample1.__dict__[field] != sample2.__dict__[field]:
                    print("Field: {} in database: {}; in spreadsheet: {}: ".format(field, sample1.__dict__[field], sample2.__dict__[field]))
                    same_objects = False

        return same_objects