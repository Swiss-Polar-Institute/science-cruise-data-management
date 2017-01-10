from django.core.management.base import BaseCommand, CommandError
from main.models import Sample, Ship, Mission, Leg, Project, Person, Event, Preservation
import csv
import glob
import codecs


class Command(BaseCommand):
    help = 'Adds data to the sample table'

    def add_arguments(self, parser):
        parser.add_argument('directory_name', type=str)

    def handle(self, *args, **options):
        #print(options['directory_name'])
        self.import_data_from_directory(options['directory_name'])

    def import_data_from_directory(self, directory_name):
        for file in glob.glob(directory_name + "/*.csv"):
            print("PROCESSING FILES: " + directory_name + "/*.csv")
            self.import_data_from_csv(file)

    def import_data_from_csv(self, filepath):
        with codecs.open(filepath, encoding = 'utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)

            rows = 0
            skipped = 0
            inserted = 0
            identical = 0
            replaced = 0
            rows_with_errors = 0

            for row in reader:
                print("Processing file: ", filepath)
                print(row)
                sample = Sample()
                sample.expedition_sample_code = row['ace_sample_number']
                sample.project_sample_number = row['project_sample_number']
                sample.contents = row['contents']
                sample.crate_number = row['crate_number']
                sample.storage_type = row['storage_type']
                sample.storage_location = row['storage_location']
                sample.offloading_port = row['offloading_port']
                sample.destination = row['destination']

                code_string = sample.expedition_sample_code.split('/')[0]
                mission_acronym_string = sample.expedition_sample_code.split('/')[1]
                leg_string = sample.expedition_sample_code.split('/')[2]
                project_number_string = sample.expedition_sample_code.split('/')[3]
                julian_day = int(sample.expedition_sample_code.split('/')[4])
                pi_initials_string = sample.expedition_sample_code.split('/')[6]
                event_number_string = int(sample.expedition_sample_code.split('/')[5])

                ship_queryset = Ship.objects.filter(shortened_name=code_string)
                # print(ship_queryset)
                mission_queryset = Mission.objects.filter(acronym=mission_acronym_string)
                # print(mission_queryset)
                leg_queryset = Leg.objects.filter(number=leg_string)
                # print(leg_queryset)
                project_queryset = Project.objects.filter(number=project_number_string)
                # print(project_queryset)
                # print(julian_day)
                person_queryset = Person.objects.filter(initials=pi_initials_string)
                # print(person_queryset)
                event_queryset = Event.objects.filter(number=event_number_string)
                # print(event_queryset)
                preservation_queryset = Preservation.objects.filter(name=row['preservation'])

                how_many_errors_have_ocurred = 0

                if len(event_queryset) != 1:
                    self.report_error(row, event_queryset, 'event', event_number_string)
                    how_many_errors_have_ocurred += 1

                if len(ship_queryset) != 1:
                    self.report_error(row, ship_queryset, 'ship', code_string)
                    how_many_errors_have_ocurred += 1

                if len(mission_queryset) != 1:
                    self.report_error(row, mission_queryset, 'mission', mission_acronym_string)
                    how_many_errors_have_ocurred += 1

                if len(leg_queryset) !=1:
                    self.report_error(row, leg_queryset, 'leg', leg_string)
                    how_many_errors_have_ocurred += 1

                if len(project_queryset) != 1:
                    self.report_error(row, project_queryset, 'project', project_number_string)
                    how_many_errors_have_ocurred += 1

                if len(person_queryset) != 1:
                    self.report_error(row, person_queryset, 'person', pi_initials_string)
                    how_many_errors_have_ocurred += 1

                if row['preservation'] != '' and len(preservation_queryset) != 1:
                    self.report_error(row, preservation_queryset, 'preservation', row['preservation'])
                    how_many_errors_have_ocurred += 1

                rows += 1

                if how_many_errors_have_ocurred == 0:
                    event = event_queryset[0]
                    ship = ship_queryset[0]
                    mission = mission_queryset[0]
                    leg = leg_queryset[0]
                    project = project_queryset[0]
                    pi_initials = person_queryset[0]

                    sample.ship = ship
                    sample.mission = mission
                    sample.leg = leg
                    sample.project = project
                    sample.julian_day = julian_day
                    sample.event = event
                    sample.pi_initials = pi_initials

                    if row['preservation'] != '':
                        sample.preservation = preservation_queryset[0]

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
                else:
                    input("Press enter to continue")
                    rows_with_errors += 1

                print("TOTAL ROWS PROCESSED= ",rows, "; Inserted = ", inserted, "; Identical = ", identical, "; Skipped = ", skipped, "; Replaced = ", replaced, "; Rows with errors = ", rows_with_errors)

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
            if field != '_state' and field != 'id':
                if sample1.__dict__[field] != sample2.__dict__[field]:
                    print("Field: {} in database: {}; in spreadsheet: {}: ".format(field, sample1.__dict__[field], sample2.__dict__[field]))
                    same_objects = False

        return same_objects
