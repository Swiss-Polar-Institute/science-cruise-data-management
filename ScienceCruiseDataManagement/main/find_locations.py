from main import utils


def find_locations(ship_date_time, ship_date_times):
    ship_date_times = ship_date_times.replace("\r", "")

    # The single location
    single_location = ship_location(ship_date_time)

    latitude = single_location['latitude']
    longitude = single_location['longitude']
    date_time = single_location['date_time']

    if latitude is None or longitude is None or date_time is None:
        latitude = longitude = "Unknown"

    message = single_location['message']


    # List of locations
    list_of_locations = []
    if len(ship_date_times) > 10:
        for ship_date_time in ship_date_times.split("\n"):
            location = ship_location(ship_date_time)

            if location['latitude'] is None or location['longitude'] is None:
                location['latitude'] = ""
                location['longitude'] = ""
                location['date_time'] = "invalid"


            information = {'date_time': location['date_time'],
                           'latitude': location['latitude'],
                           'longitude': location['longitude']
                           }
            list_of_locations.append(information)

    template_information = {
        'ship_date_time': date_time,
        'latitude': latitude,
        'longitude': longitude,
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

