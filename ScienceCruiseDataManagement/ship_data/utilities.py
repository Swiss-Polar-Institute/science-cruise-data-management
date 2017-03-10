import unittest
import datetime

def nmea_degrees_to_decimal_degrees(nmea_degrees):
    decimal_position = nmea_degrees.find(".")
    minutes = nmea_degrees[decimal_position-2:]
    degrees = nmea_degrees[0:decimal_position-2]

    return float(degrees) + float(minutes)/60

def nmea_lat_long_to_normal(latitude, north_south,
                            longitude, east_west):
    """ Converts:
         From: "3550.28461074,S,01801.84299457,E" # a string
           To: (-35.838000,18.030666)             # a tuple
        Note that the parameters in the previous string would be:
                latitude=3550.28461074
                north_south=S
                longitude=01801.84299457
                east_west=E
    """

    latitude_degrees = nmea_degrees_to_decimal_degrees(latitude)
    longitude_degrees = nmea_degrees_to_decimal_degrees(longitude)

    if north_south == "S":
        latitude_degrees *= -1
    elif north_south == "N":
        pass
    else:
        assert False

    if east_west == "W":
        longitude_degrees *= -1
    elif east_west == "E":
        pass
    else:
        assert False

    return (latitude_degrees, longitude_degrees)

if __name__ == "__main__":
    assert nmea_lat_long_to_normal("3550.28461074","S","01801.84299457","E") \
           == (-35.83807684566667, 18.030716576166668)


def check_lat_lon_direction(north_south, east_west):
    '''Check that the latitude and longitude direction eg. N, S, E, W is valid.'''
    if (north_south == 'N' or north_south =='S') and (east_west =='E' or east_west == 'W'):
        return True
    else:
        return False


def string_date_time_to_tuple(date_time_string):
    '''Convert string formatted date and time to integers which can then be handled by the python module, datetime.'''
    [date, time] = date_time_string.split(' ')

    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])

    hour = int(time.split(':')[0])
    minute = int(time.split(':')[1])
    second = int(time.split(':')[2])

    utc = datetime.timezone(datetime.timedelta(0))
    millions_of_sec = 0

    return (year, month, day, hour, minute, second, millions_of_sec, utc)

