from django.core.management.base import BaseCommand, CommandError
from ship_data.models import MetDataAll, MetDataWind
import csv
from ship_data import utilities
import datetime


class Command(BaseCommand):
    help = 'Adds data to the person table'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'])

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)


    def handle(self, *args, **options):
        print(options['filename'])
        self.import_data_from_csv(options['filename'])

    header=0
    def import_data_from_csv(self, filename):
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter = "\t")
            line_number=0
            for row in reader:
                if (len(row) == 59) and line_number != 0:
                    d = {}
                    (DATE_TIME, LAT, LAT_NS, LONG, LONG_EW, d['WD2MA1'], d['WD2MM1'], d['WD2MX1'], d['WS2MA1'], d['WS2MM1'], d['WS2MX1'], d['WD10MA1'], d['WD10MM1'], d['WD10MX1'], d['WS10MA1'], d['WS10MM'], d['WS10MX1'],
                     d['WD2MA2'], d['WD2MM2'], d['WD2MX2'], d['WS2MA2'], d['WS2MM2d'], d['WS2MX2'], d['WD10MA2'],  d['WD10MX2'], d['WD10MM2'], d['WS10MA2'], d['WS10MX2'], d['WS10MM2'], d['VIS'], d['wawa'],  d['CL1'], d['CL2'], d['CL3'], d['SC1'],
                     d['SC2'], d['SC3'], d['RH1'], d['TA1'],  d['DP1'], d['RH2'], d['TA2'], d['DP2'], d['PA1'], d['PA2'], d['SR1'], d['SR2'], d['SR3'], d['UV1'], d['UV2'],  d['cond'], d['salinity'], d['TwTwTw'], d['TIMEDIFF'], d['Year'], d['Month'], d['DAY'],
                     d['CLOUDTEXT'], d['VISCODE']) = row

                    outcome_lat_lon = utilities.check_lat_lon_direction(LAT_NS, LONG_EW)
                    outcome_date_time = check_value(DATE_TIME)

                    if outcome_lat_lon == True and outcome_date_time == True:
                        (d['latitude'], d['longitude']) = utilities.nmea_lat_long_to_normal(LAT, LAT_NS, LONG, LONG_EW)
                        (year, month, day, hour, minute, second, millions_of_sec) = utilities.string_date_time_to_tuple(DATE_TIME)
                        print(year, month, day, hour, minute, second, millions_of_sec)
                        d['date_time'] = datetime.datetime(year, month, day, hour, minute, second, millions_of_sec)

                        change_dictionary_contents(d)

                        met_data_all = MetDataAll()
                        print(d)

                        met_data_all.save()
                    else:
                        print("Row skipped, invalid NS or EW, or datetime missing: ", d)

                elif (len(row) == 16) and line_number != 0:
                    d = {}
                    (TIME, d['COG'], d['HEADING'], d['WDR1'], d['WSR1'], d['WD1'], d['WS1'], d['WDR2'], d['WSR2'], d['WD2'], d['WS2'], d['TIMEDIFF'], Year, Month, DAY, d['CLOUDTEXT']) = row

                    outcome_date_time = check_value(TIME)

                    if outcome_date_time == True:
                        d['date_time'] = datetime.datetime(utilities.string_date_time_to_tuple(TIME))
                        change_dictionary_contents(d)

                        met_data_wind = MetDataWind()
                        print(d)
                        met_data_wind.save()

                else:
                    print("Row skipped: ", row)

                line_number = line_number+1


def change_dictionary_contents(d):
    for key in d.keys():
        if d[key] == '///' or d[key] == '' or d[key] == '//':
            d[key] = None

def check_value(variable):
    if variable == '':
        return False
    else:
        return True