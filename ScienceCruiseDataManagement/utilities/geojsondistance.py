#!/usr/bin/python3

import geojson
from geopy.distance import vincenty
from geopy.distance import great_circle
import random
import math

def calculate_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6356.752  # km
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
    if previous is not None:
        distance += calculate_distance(previous, item)
        print(vincenty(previous, item).kilometers, item)

    previous = item

print(distance)

previous = None
distance = 0
for item in g.get('coordinates'):
    if previous is not None:
            distance += vincenty(previous, item).kilometers
            print(vincenty(previous, item).kilometers, item)

    previous = item

print(distance)


previous = None
distance = 0
for item in g.get('coordinates'):
    if previous is not None:
            distance += great_circle(previous, item).kilometers

    previous = item

print(distance)
