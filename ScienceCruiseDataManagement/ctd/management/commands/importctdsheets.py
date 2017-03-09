from django.core.management.base import BaseCommand, CommandError
from ctd.models import CtdVariable, CtdSampleVolume, CtdBottleTrigger
from main.models import CtdCast, Person, Event, Leg
import csv
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

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


def import_ctd_sample_variables(all_file, ctd_cast):
    niskin = last_int_row_col(all_file, 9, 'C')

    while True:
        row = 8 + niskin

        if row >= len(all_file) or \
            last_str_row_col(all_file, row, 'C') != last_str_row_col(all_file, row, 'C') != str(niskin) or \
            last_str_row_col(all_file, row, 'C') == "":
            break

        ctd_bottle_trigger = CtdBottleTrigger()
        ctd_bottle_trigger.ctd_cast = ctd_cast

        depth_triggered = all_file[row][col_letter_to_index('A')]
        depth_planned = all_file[row][col_letter_to_index('B')]
        comment = all_file[row][col_letter_to_index('W')]

        try:
            depth = int(depth_triggered)
        except ValueError:
            try:
                depth = int(depth_planned)
            except ValueError:
                # end of sample sheet
                break

        ctd_bottle_trigger.depth = depth
        ctd_bottle_trigger.niskin = niskin

        if comment != "":
            ctd_bottle_trigger.comment = comment

        ctd_bottle_trigger.save()

        col_index = col_letter_to_index('F')

        while True:
            volume = all_file[row][col_index]
            variable = all_file[7][col_index]

            if variable == "Available Vol (L)":
                break

            ctd_sample_volume = CtdSampleVolume()
            ctd_sample_volume.ctd_bottle_trigger = ctd_bottle_trigger
            ctd_sample_volume.ctd_variable = CtdVariable.objects.get(name=variable)

            if volume == 'x':
                ctd_sample_volume.volume = None
                ctd_sample_volume_to_be_saved = True
            elif volume == '':
                ctd_sample_volume.volume = None
                ctd_sample_volume_to_be_saved = False
            else:
                ctd_sample_volume.volume = float(volume)
                ctd_sample_volume_to_be_saved = True

            if ctd_sample_volume_to_be_saved is not None:
                ctd_sample_volume.ctd_bottle_trigger = ctd_bottle_trigger
                ctd_sample_volume.save()

                print("CTD sample volume: {}".format(ctd_sample_volume))

            col_index += 1

        niskin += 1


def text_to_person(text):
    return None


def last_str_row_col(all_file, row, col):
    assert row-1 >= 0
    assert col_letter_to_index(col) >= 0

    return all_file[row-1][col_letter_to_index(col)].split(" ")[-1]


def last_int_row_col(all_file, row, col):
    string = last_str_row_col(all_file, row, col)

    try:
        int(string)
    except ValueError:
        print("String is not convertible to int:", string)
        assert False

    return int(last_str_row_col(all_file, row, col))


def name_to_person(name):
    print(name)
    if name == "Thalia":
        name_last = "Henry"
    elif name == "MNH":
        name_last = "Houssais"
    else:
        assert False

    return Person.objects.get(name_last=name_last)

def create_ctd_cast(all_file, filename):
    ctd_cast = CtdCast()

    ctd_cast.ctd_cast_number = last_int_row_col(all_file, 2, 'A')
    ctd_cast.event_number = Event.objects.all().get(number=last_int_row_col(all_file, 4, 'A'))
    ctd_cast.ctd_operator = name_to_person(last_str_row_col(all_file, 5, 'A'))

    ctd_cast.ctd_file_name = last_str_row_col(all_file, 6, 'A')
    ctd_cast.ice_coverage = last_int_row_col(all_file, 5, 'F')

    if "Leg2" in filename:
        ctd_cast.leg_number = Leg.objects.all().get(number=2)
    elif "Leg3" in filename:
        ctd_cast.leg_number = Leg.objects.all().get(number=2)
    else:
        assert False

    ctd_cast.save()

    return ctd_cast


def import_ctd_sheet(filename):
    fp = open(filename, "r")
    csv_file = csv.reader(fp)

    all_file = read_all(csv_file)

    import_ctd_variables(all_file)

    event = all_file[3][col_letter_to_index('A')]
    assert event.startswith("Event # ")
    event_number = last_int_row_col(all_file, 4, 'A')

    try:
        ctd_cast = CtdCast.objects.get(event_number=event_number)
    except ObjectDoesNotExist:
        ctd_cast = create_ctd_cast(all_file, filename)

    import_ctd_sample_variables(all_file, ctd_cast)
