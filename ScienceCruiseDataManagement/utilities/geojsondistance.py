#!/usr/bin/python3

import geojson

import math

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
    if previous is not None:
        distance += calculate_distance(previous, item)

    previous = item

print(distance)