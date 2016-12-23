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