import unittest

def nmea_lat_long_to_normal(nmea_lat_long):
    """ Converts:
         From: "3550.28461074,S,01801.84299457,E" # a string
           To: (-35.838000,18.030666)             # a tuple
    """

    nmea_lat_long = nmea_lat_long.split(",")

    latitude = nmea_lat_long[0]
    longitude = nmea_lat_long[2]

    north_south = nmea_lat_long[1]
    east_west = nmea_lat_long[3]

    latitude_degrees = float(latitude[0:2]) + ((float(latitude[2:])) / 60)
    longitude_degrees = float(longitude[0:3]) + ((float(longitude[3:])) / 60)

    if north_south == "S":
        latitude_degrees *= -1

    if east_west == "E":
        longitude_degrees *= -1

    return (latitude_degrees, longitude_degrees)

if __name__ == "__main__":
    assert nmea_lat_long_to_normal("3550.28461074,S,01801.84299457,E") \
           == (-35.83807684566667, -18.030716576166668)