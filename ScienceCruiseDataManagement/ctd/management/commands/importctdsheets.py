from django.core.management.base import BaseCommand, CommandError
from ctd.models import CtdVariable, CtdSampleVolume, CtdBottleTrigger
from main.models import CtdCast, Person, Event, Leg
import csv
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import glob
import os
import re

# Note that this script will no longer work in the way that the CTD.Ctdvariable model is now set up (2017-09-21).The model has been changed to add in foreign keys in an effort to remove the names from the sample variable column, therefore this script will need altering to take the PI names and get that from the main.person table, and the variable from the list of variables which have had the duplication removed from the list.

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
    help = 'Import CTD sheets'

    def add_arguments(self, parser):
        parser.add_argument('basedirectory', type=str)

    def handle(self, *args, **options):
        basedirectory = options['basedirectory']

        if os.path.isdir(basedirectory):
            for filename in glob.glob(os.path.join(basedirectory, "*")):
                import_ctd_sheet(filename)
        else:
            import_ctd_sheet(basedirectory)

def read_all(csv_file):
    file = []

    for line in csv_file:
        file.append(line)

    return file


def col_letter_to_index(column):
    # only works to Z
    return ord(column.upper()) - ord('A')


def import_ctd_variables(all_file):
    column = first_column_data(all_file)
    row = row_for_depth(all_file)

    while True:
        variable_name = str_row_col(all_file, row, column).lower()

        if variable_name == "available vol (l)" or variable_name == "available volume (l)":
            break

        ctd_variable = CtdVariable()
        ctd_variable.name = variable_name

        try:
            ctd_variable.save()
        except IntegrityError:
            pass

        column = chr(ord(column)+1)


def row_for_depth(all_file):
    row_number = 1

    for row in all_file:
        text = row[0].replace(" ", "").lower()
        if text == "depth(m)" or text == "triggerdepth(m)" or text == "actualdepth(m)":
            return row_number
        row_number += 1

    assert False


def calculate_column_index_for_comment(all_file):
    headers_row = row_for_depth(all_file)

    row = all_file[headers_row-1]

    for (i, cell) in enumerate(row):
        if cell == "Comments":
            return i

    print("Comments column not found")
    assert False


def column_for_niskin_number(all_file):
    headers_row = row_for_depth(all_file)

    row = all_file[headers_row-1]

    column = 'A'
    for cell in row:
        if cell == "Niskin #":
            return column

        column = chr(ord(column)+1)

    return column


def first_column_data(all_file):
    headers_row = row_for_depth(all_file)

    row = all_file[headers_row-1]

    column = 'A'
    previous_cell = None
    for cell in row:
        if cell != "" and previous_cell == "":
            return column
        elif cell == "Bottle Integrity":
            return chr(ord(column)+1)

        previous_cell = cell
        column = chr(ord(column) + 1)

    return column


def import_ctd_sample_variables(all_file, ctd_cast):
    column_niskin_numbers = column_for_niskin_number(all_file)
    niskin = last_int_row_col(all_file, row_for_depth(all_file)+1, column_niskin_numbers)

    while True:
        row = row_for_depth(all_file) + niskin
        niskin_cell_contents = str_row_col(all_file, row, column_niskin_numbers)

        # some niskin bottles might have comments
        niskin_cell_contents = re.sub("[^0-9]", "", niskin_cell_contents)

        assert str(niskin) == str(niskin_cell_contents)

        if row >= len(all_file) or \
            last_str_row_col(all_file, row, 'C') != last_str_row_col(all_file, row, 'C') != str(niskin) or \
            last_str_row_col(all_file, row, 'C') == "":
            break

        ctd_bottle_trigger = CtdBottleTrigger()
        ctd_bottle_trigger.ctd_cast = ctd_cast

        depth_triggered = all_file[row][col_letter_to_index('A')]
        depth_planned = all_file[row][col_letter_to_index('B')]

        column_index_for_comment = calculate_column_index_for_comment(all_file)

        comment = all_file[row][column_index_for_comment]

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

        try:
            ctd_bottle_trigger.save()
        except IntegrityError:
            ctd_bottle_trigger = CtdBottleTrigger.objects.filter(ctd_cast=ctd_cast).filter(depth=depth).filter(niskin=niskin)[0]
            ctd_bottle_trigger.comment = comment
            ctd_bottle_trigger.save()

        col_index = col_letter_to_index(first_column_data(all_file))

        while True:
            volume = all_file[row][col_index]
            variable = all_file[row_for_depth(all_file)-1][col_index]

            lowercase_variable = variable.lower()
            if lowercase_variable == "available vol (l)" or lowercase_variable == "available volume (l)":
                break

            ctd_sample_volume = CtdSampleVolume()
            ctd_sample_volume.ctd_bottle_trigger = ctd_bottle_trigger
            ctd_variable = CtdVariable.objects.get(name=variable)
            ctd_sample_volume.ctd_variable = ctd_variable

            if volume == 'x':
                volume = None
                ctd_sample_volume_to_be_saved = True
            elif volume == '':
                volume = None
                ctd_sample_volume_to_be_saved = False
            else:
                volume = float(volume)
                ctd_sample_volume_to_be_saved = True

            ctd_sample_volume.volume = volume
            if ctd_sample_volume_to_be_saved:
                ctd_sample_volume.ctd_bottle_trigger = ctd_bottle_trigger
                try:
                    ctd_sample_volume.save()
                except IntegrityError:
                    ctd_sample_volume = CtdSampleVolume.objects.filter(ctd_bottle_trigger=ctd_bottle_trigger).filter(ctd_variable=ctd_variable)
                    ctd_sample_volume.volume = volume

            col_index += 1

        niskin += 1


def text_to_person(text):
    return None


def last_str_row_col(all_file, row, col):
    assert row-1 >= 0
    assert col_letter_to_index(col) >= 0

    return all_file[row-1][col_letter_to_index(col)].split(" ")[-1]


def str_row_col(all_file, row, col):
    assert row-1 >= 0
    assert col_letter_to_index(col) >= 0

    return all_file[row-1][col_letter_to_index(col)]


def last_int_row_col(all_file, row, col):
    string = last_str_row_col(all_file, row, col)

    try:
        int(string)
    except ValueError:
        assert False

    return int(last_str_row_col(all_file, row, col))


def name_to_person(name):
    name = name.replace(" ", "").lower()
    print(name)
    if "_________" in name:
        return None
    elif name == "thalia" or name == "tahlia":
        name_last = "Henry"
    elif name == "mnh":
        name_last = "Houssais"
    elif name == "Jenny":
        name_last = "Hutchings"
    elif name == "":
        return None
    else:
        print("Can't find the name _{}_".format(name))
        assert False

    return Person.objects.get(name_last=name_last)

def find_string(all_csv, label, none_if_not_found=False):
    for row in all_csv:
        for cell in row:
            if cell.startswith(label):
                return cell[len(label):].strip()

    if none_if_not_found:
        return None
    else:
        assert False

def create_ctd_cast(all_file, filename):
    ctd_cast = CtdCast()

    # ctd_cast.ctd_cast_number = last_int_row_col(all_file, 2, 'A')
    # ctd_cast.event_number = Event.objects.all().get(number=last_int_row_col(all_file, 4, 'A'))
    # ctd_cast.ctd_operator = name_to_person(last_str_row_col(all_file, 5, 'A'))
    #
    # ctd_cast.ctd_file_name = last_str_row_col(all_file, 6, 'A')
    # ctd_cast.ice_coverage = last_int_row_col(all_file, 5, 'F')

    ctd_cast.ctd_cast_number = find_string(all_file, 'Cast #')
    ctd_cast.event_number = Event.objects.all().get(number=find_string(all_file, "Event #"))
    ctd_cast.ctd_operator = name_to_person(find_string(all_file, "CTD Operator"))

    ctd_cast.ctd_file_name = find_string(all_file, "CTD file:", none_if_not_found=True)
    if "leg1" in filename.lower():
        ctd_cast.leg_number = Leg.objects.all().get(number=1)
    if "leg2" in filename.lower():
        ctd_cast.leg_number = Leg.objects.all().get(number=2)
    elif "leg3" in filename.lower():
        ctd_cast.leg_number = Leg.objects.all().get(number=3)
    else:
        assert False

    try:
        ctd_cast.save()
    except IntegrityError:
        print("Integrity error:", ctd_cast)


    return ctd_cast


def import_ctd_sheet(filename):
    print("Filename:", filename)
    fp = open(filename, "r")
    csv_file = csv.reader(fp)

    all_file = read_all(csv_file)

    import_ctd_variables(all_file)

    event_number = find_string(all_file, "Event #")

    try:
        ctd_cast = CtdCast.objects.get(event_number=event_number)
    except ObjectDoesNotExist:
        ctd_cast = create_ctd_cast(all_file, filename)

    import_ctd_sample_variables(all_file, ctd_cast)
