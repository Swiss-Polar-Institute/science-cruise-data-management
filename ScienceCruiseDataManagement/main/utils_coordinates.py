import re


def pretty_name(name):
    if name == "decimal_degrees":
        return "Decimal degrees"
    elif name == "decimal_degrees_minutes":
        return "Degrees and decimal minutes"
    elif name == "decimal_degrees_minutes_seconds":
        return "Degrees, minutes and decimal seconds"


def coordinates_formats():
    return ["decimal_degrees", "decimal_degrees_minutes", "decimal_degrees_minutes_seconds"]


def detect_name_coordinate(coordinate):
    if re.match("^-{0,1}[0-9]+\.[0-9]+ -{0,1}[0-9]+\.[0-9]+$", coordinate):
        return "decimal_degrees"
    elif re.match("^[0-9]+ [0-9]+\.[0-9]+ [NS] [0-9]+ [0-9]+\.[0-9]+ [EW]$", coordinate):
        return "decimal_degrees_minutes"
    elif re.match("^[0-9]+ [0-9]+ [0-9]+\.[0-9]+ [NS] [0-9]+ [0-9]+ [0-9]+\.[0-9]+ [EW]$", coordinate):
        return "decimal_degrees_minutes_seconds"
    else:
        return None


def convert_to_decimal_degrees(coordinate):
    type_of_coordinate = detect_name_coordinate(coordinate)

    if type_of_coordinate == "decimal_degrees":
        (latitude, longitude) = coordinate.split(" ")
        latitude = float(latitude)
        longitude = float(longitude)
        return (latitude, longitude)

    elif type_of_coordinate == "decimal_degrees_minutes":
        m = re.match("(^[0-9]+) ([0-9]+\.[0-9]+) ([NS]) ([0-9]+) ([0-9]+\.[0-9]+) ([EW])$", coordinate)
        latitude = float(m.group(1)) + float(m.group(2))/60
        if m.group(3) == "S":
            latitude = latitude * -1

        longitude = float(m.group(4)) + float(m.group(5))/60
        if m.group(6) == "W":
            longitude = longitude * -1

        return (latitude, longitude)

    elif type_of_coordinate == "decimal_degrees_minutes_seconds":
        m = re.match("^([0-9]+) ([0-9]+) ([0-9]+\.[0-9]+) ([NS]) ([0-9]+) ([0-9]+) ([0-9]+\.[0-9]+) ([EW])$", coordinate)

        latitude = float(m.group(1))
        latitude = latitude + float(m.group(2))/60
        latitude = latitude + float(m.group(3)) / 3600

        if m.group(4) == "S":
            latitude = latitude * -1
        elif m.group(4) == "N":
            pass
        else:
            assert False

        longitude = float(m.group(5))
        longitude = longitude + float(m.group(6)) / 60
        longitude = longitude + float(m.group(7)) / 3600

        if m.group(8) == "W":
            longitude = longitude * -1
        elif m.group(8) == "E":
            pass
        else:
            assert False


        return (latitude, longitude)


def convert_decimal_degrees_to(coordinate, type_of_coordinates):
    if type_of_coordinates == "decimal_degrees":
        return ("{:.3f} {:.3f}".format(coordinate[0], coordinate[1]))

    elif type_of_coordinates == "decimal_degrees_minutes":
        (latitude_degree, latitude_minute, latitude_decimal_minute,
         latitude_second, latitude_sign) = calc_degreeminutes(coordinate[0])

        (longitude_degree, longitude_minute, longitude_decimal_minute,
         longitude_second, longitude_sign) = calc_degreeminutes(coordinate[1])

        if latitude_sign == -1:
            hemisphere = "S"
        else:
            hemisphere = "N"

        if longitude_sign == -1:
            side = "W"
        else:
            side = "E"


        latitude_string = "{:.0f} {:.3f} {}".format(latitude_degree, latitude_decimal_minute, hemisphere)
        longitude_string = "{:.0f} {:.3f} {}".format(longitude_degree, longitude_decimal_minute, side)

        return "{} {}".format(latitude_string, longitude_string)

    elif type_of_coordinates == "decimal_degrees_minutes_seconds":
        (latitude_degree, latitude_minute, latitude_decimal_minute,
         latitude_second, latitude_sign) = calc_degreeminutes(coordinate[0])

        (longitude_degree, longitude_minute, longitude_decimal_minute,
         longitude_second, longitude_sign) = calc_degreeminutes(coordinate[1])

        if latitude_sign == -1:
            hemisphere = "S"
        else:
            hemisphere = "N"

        if longitude_sign == -1:
            side = "W"
        else:
            side = "E"

        latitude_string = "{:.0f} {:.0f} {:.3f} {}".format(latitude_degree, latitude_minute, latitude_second, hemisphere)
        longitude_string = "{:.0f} {:.0f} {:.3f} {}".format(longitude_degree, longitude_minute, latitude_second, side)

        return "{} {}".format(latitude_string, longitude_string)

    else:
        assert False


def convert_to(coordinate, format):
    coordinate_in_decimal = convert_to_decimal_degrees(coordinate)

    return convert_decimal_degrees_to(coordinate_in_decimal, format)


def process(coordinates, template_information):
    coordinates = coordinates.replace("\r", "")

    previous_name_coordinate = None

    template_information['list_of_coordinates'] = []

    for coordinate in coordinates.split("\n"):
        coordinate = coordinate.strip()
        if coordinate == "":
            continue

        name_coordinate = detect_name_coordinate(coordinate)
        if name_coordinate is None:
            template_information["error"] = "Coordinate: '{}' is not in a valid format. Aborts.".format(coordinate)
            break
        formats = coordinates_formats()

        formats.remove(name_coordinate)

        if name_coordinate == None:
            template_information["error"] = "Invalid type of coordinate: {}. Aborted.".format(coordinate)
            return
        if previous_name_coordinate is not None and name_coordinate != previous_name_coordinate:
            template_information["error"] = "Coordinate {} is a different type than previous one. Aborted.".format(coordinate)
            return

        previous_name_coordinate = name_coordinate

        template_information['input_format_name'] = pretty_name(name_coordinate)
        template_information['output_format_name1'] = pretty_name(formats[0])
        template_information['output_format_name2'] = pretty_name(formats[1])

        template_information['list_of_coordinates'].append({"input": coordinate,
                                                            "output1": convert_to(coordinate, formats[0]),
                                                            "output2": convert_to(coordinate, formats[1])
                                                            })

    print("Coordinates:", coordinates)


def cmp(a,b):
    return (a > b) - (a < b)


def calc_degreeminutes(decimal_degree):
    # Code from LatLong package. The LatLong package is not Python3
    # compatible so we took what we needed only
    '''
    Calculate degree, minute second from decimal degree
    '''
    sign = cmp(decimal_degree, 0) # Store whether the coordinate is negative or positive
    decimal_degree = abs(decimal_degree)
    degree = decimal_degree//1 # Truncate degree to be an integer
    decimal_minute = (decimal_degree - degree)*60. # Calculate the decimal minutes
    minute = decimal_minute//1 # Truncate minute to be an integer
    second = (decimal_minute - minute)*60. # Calculate the decimal seconds
    # Finally, re-impose the appropriate sign
    degree = degree
    minute = minute
    second = second
    return (degree, minute, decimal_minute, second, sign)
