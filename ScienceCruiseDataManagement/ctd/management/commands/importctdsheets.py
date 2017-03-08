from django.core.management.base import BaseCommand, CommandError
from ctd.models import CtdVariable, CtdSampleVariable, CtdBottleTrigger
from main.models import CtdCast
import csv
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Import CTD sheets'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        filename = options['filename']
        import_ctd_sheet(filename)

def read_all(csv_file):
    file = []

    for line in csv_file:
        file.append(line)

    return file


def col_letter_to_index(column):
    # only works to Z
    return ord(column.upper()) - ord('A')


def import_ctd_variables(all_file):
    for col_index in range(col_letter_to_index('F'), col_letter_to_index('U')):
        ctd_variable = CtdVariable()
        ctd_variable.name = all_file[7][col_index]
        try:
            ctd_variable.save()
        except IntegrityError:
            pass


def import_ctd_sample_variables(all_file, event_number):
    niskin = 1

    while niskin <= 24:
        row = 7+niskin
        col = col_letter_to_index('C')
        assert str(all_file[row][col]) == str(niskin)

        ctd_bottle_trigger = CtdBottleTrigger()
        ctd_bottle_trigger.ctd_cast = CtdCast.objects.get(event_number=event_number)

        depth_triggered = all_file[row][col_letter_to_index('A')]
        depth_planned = all_file[row][col_letter_to_index('B')]

        try:
            depth = int(depth_triggered)
        except ValueError:
            depth = int(depth_planned)

        ctd_bottle_trigger.depth = depth
        ctd_bottle_trigger.niskin = niskin
        ctd_bottle_trigger.save()

        if all_file[row][col+1] != "":  # it has been fired
            for col_index in range(col_letter_to_index('E'), col_letter_to_index('U')):
                volume = all_file[row][col_index]
                variable = all_file[7][col_index]



                print(volume, variable)

        niskin += 1

def import_ctd_sheet(filename):
    fp = open(filename, "r")
    csv_file = csv.reader(fp)

    all_file = read_all(csv_file)

    import_ctd_variables(all_file)

    event = all_file[3][col_letter_to_index('A')]
    assert event.startswith("Event # ")
    event_number = int(event.split(" ")[-1])
    import_ctd_sample_variables(all_file, event_number)
