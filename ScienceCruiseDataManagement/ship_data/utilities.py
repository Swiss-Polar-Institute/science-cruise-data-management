import unittest

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

    latitude_degrees = float(latitude[0:2]) + ((float(latitude[2:])) / 60)
    longitude_degrees = float(longitude[0:3]) + ((float(longitude[3:])) / 60)

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
    assert nmea_lat_long_to_normal("3550.28461074,S,01801.84299457,E") \
           == (-35.83807684566667, 18.030716576166668)


def check_lat_lon_direction(north_south, east_west):
    '''Check that the latitude and longitude direction eg. N, S, E, W is valid.'''
    if (north_south == 'N' or north_south =='S') and (east_west =='E' or east_west == 'W'):
        return True
    else:
        return False


def string_date_time_to_tuple(date_time_string):
    '''Convert string formatted date and time to integers which can then be handled by the python module, datetime.'''
    year = int(date_time_string[0:3])
    month = int(date_time_string[5:6])
    day = int(date_time_string[8:9])
    hour = int(date_time_string[11:12])
    minute = int(date_time_string[14:15])
    seconds = int(date_time_string[17:])

        # Some GPS sources have the time with hundreds of seconds like.
        # HHMMSS.tt . Some don't have the ".tt"
    if "." in date_time_string:
        millions_of_sec = int(date_time_string.split(".")[1])*10000
    else:
        millions_of_sec = 0

    return (year, month, day, hour, minute, seconds, millions_of_sec)

