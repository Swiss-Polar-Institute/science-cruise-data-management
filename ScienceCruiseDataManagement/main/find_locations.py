from main import utils
from main import utils_coordinates

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

def find_locations(ship_date_time, ship_date_times):
    ship_date_times = ship_date_times.replace("\r", "")

    # The single location
    single_location = ship_location(ship_date_time)

    latitude_decimal_degrees_single_location = single_location['latitude']
    longitude_decimal_degrees_single_location = single_location['longitude']
    date_time = single_location['date_time']

    if latitude_decimal_degrees_single_location is None or longitude_decimal_degrees_single_location is None or date_time is None:
        latitude_decimal_degrees_single_location = longitude_decimal_degrees_single_location = "Unknown"
        latitude_degrees_decimal_minutes_single_location = longitude_degrees_decimal_minutes_single_location = "Unknown"
        latitude_degrees_minutes_decimal_seconds_single_location = longitude_degrees_minutes_decimal_seconds_single_location = "Unknown"

    try:
        decimal_degrees_single_location = (float(latitude_decimal_degrees_single_location), float(longitude_decimal_degrees_single_location))
        (latitude_degrees_decimal_minutes_single_location,
         longitude_degrees_decimal_minutes_single_location) = utils_coordinates.convert_decimal_degrees_to(decimal_degrees_single_location,
                                                                                           "decimal_degrees_minutes")
        (latitude_degrees_minutes_decimal_seconds_single_location,
         longitude_degrees_minutes_decimal_seconds_single_location) = utils_coordinates.convert_decimal_degrees_to(decimal_degrees_single_location,
                                                                                                   "decimal_degrees_minutes_seconds")
    except ValueError:
        # Sadly the ship_location() can return strings - in the try code it tries to convert them to float,
        # if it fails we return this to the next level.
        pass

    message = single_location['message']

    # List of locations
    list_of_locations = []
    if len(ship_date_times) > 10:
        for ship_date_time in ship_date_times.split("\n"):
            location = ship_location(ship_date_time)

            if location['latitude'] is None or location['longitude'] is None:
                location['latitude'] = ""
                location['longitude'] = ""
                location['date_time'] = "(It was empty)"

            if ship_date_time != "":
                location['date_time'] = ship_date_time

            (latitude_decimal_degrees, longitude_decimal_degrees) = (location['latitude'], location['longitude'])
            (latitude_degrees_decimal_minutes, longitude_degrees_decimal_minutes) = (latitude_decimal_degrees, longitude_decimal_degrees)
            (latitude_degrees_minutes_decimal_seconds, longitude_degrees_minutes_decimal_seconds) = (latitude_decimal_degrees, longitude_decimal_degrees)

            try:
                decimal_degrees = (float(latitude_decimal_degrees), float(longitude_decimal_degrees))
                (latitude_degrees_decimal_minutes, longitude_degrees_decimal_minutes) = utils_coordinates.convert_decimal_degrees_to(decimal_degrees, "decimal_degrees_minutes")
                (latitude_degrees_minutes_decimal_seconds, longitude_degrees_minutes_decimal_seconds) = utils_coordinates.convert_decimal_degrees_to(decimal_degrees, "decimal_degrees_minutes_seconds")
            except ValueError:
                # Sadly the ship_location() can return strings - in the try code it tries to convert them to float,
                # if it fails we return this to the next level.
                pass

            information = {'date_time': location['date_time'],
                           'latitude_decimal_degrees': latitude_decimal_degrees,
                           'longitude_decimal_degrees': longitude_decimal_degrees,
                           'latitude_degrees_decimal_minutes': latitude_degrees_decimal_minutes,
                           'longitude_degrees_decimal_minutes': longitude_degrees_decimal_minutes,
                           'latitude_degrees_minutes_decimal_seconds': latitude_degrees_minutes_decimal_seconds,
                           'longitude_degrees_minutes_decimal_seconds': longitude_degrees_minutes_decimal_seconds
                           }
            list_of_locations.append(information)

    template_information = {
        'ship_date_time': date_time,
        'latitude_decimal_degrees_single_location': latitude_decimal_degrees_single_location,
        'longitude_decimal_degrees_single_location': longitude_decimal_degrees_single_location,
        'longitude_decimal_degrees_single_location': longitude_decimal_degrees_single_location,
        'latitude_degrees_decimal_minutes_single_location': latitude_degrees_decimal_minutes_single_location,
        'longitude_degrees_decimal_minutes_single_location': longitude_degrees_decimal_minutes_single_location,
        'latitude_degrees_minutes_decimal_seconds_single_location': latitude_degrees_minutes_decimal_seconds_single_location,
        'longitude_degrees_minutes_decimal_seconds_single_location': longitude_degrees_minutes_decimal_seconds_single_location,
        'list_of_locations': list_of_locations,
        'message': message
    }

    return template_information


def ship_location(str_datetime):
    ship_date_time = utils.string_to_date_time(str_datetime)

    if ship_date_time is None:
        date_time = None
        latitude = longitude = None
        message = "Invalid date time (format has to be YYYY-MM-DD HH:mm:SS) (or without the secs)"
    elif ship_date_time > utils.now_with_timezone():
        date_time = "FUTURE"
        latitude = longitude = None
        message = "The date time seems to be in the future. We don't know where we are going to be!"
    else:
        location = utils.ship_location(ship_date_time)
        latitude = location.latitude
        longitude = location.longitude
        date_time = location.date_time
        message = ''

    if latitude is None or longitude is None or date_time is None:
        latitude = longitude = None
    else:
        latitude = "{0:.4f}".format(latitude)
        longitude = "{0:.4f}".format(longitude)

    return {'latitude': latitude, 'longitude': longitude, 'message': message, 'date_time': date_time}

