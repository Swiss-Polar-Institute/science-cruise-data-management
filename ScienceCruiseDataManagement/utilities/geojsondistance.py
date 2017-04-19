#!/usr/bin/python3

import geojson
from geopy.distance import vincenty
from geopy.distance import great_circle
import random
import math

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

def calculate_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
                                                  * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d

g = geojson.load(open("/home/carles/track.geojson"))


previous = None
distance = 0
for item in g.get('coordinates'):
    print(item)
    if previous is not None:
            distance += vincenty((previous[1], previous[0]), (item[1], item[0])).kilometers

    previous = item

print("Vincenty:", distance)


previous = None
distance = 0
for item in g.get('coordinates'):
    if previous is not None:
        distance += calculate_distance((previous[1], previous[0]), (item[1], item[0]))

    previous = item

print("Harvesine:", distance)

previous = None
distance = 0
for item in g.get('coordinates'):
    if previous is not None:
            distance += great_circle((previous[1], previous[0]), (item[1], item[0])).kilometers

    previous = item

print("Great circle:", distance)
