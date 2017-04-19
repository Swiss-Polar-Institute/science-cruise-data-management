import gpxpy
from .models import Station, Leg, StationType

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

def import_gpx_to_stations(gpx_as_string):
    gpx = gpxpy.parse(gpx_as_string)

    total_modified = 0
    total_created = 0
    total_skipped = 0
    reports = []

    current_leg = Leg.current_active_leg()
    station_type = StationType.objects.get(id=1)

    for route in gpx.routes:
        for point in route.points:
            # station = Station()
            # station.latitude = waypoint.latitude
            # station.longitude = waypoint.longitude
            # station.name = waypoint.name
            # station.leg = Leg.current_active_leg()

            waypoint_information = {
                'latitude': point.latitude,
                'longitude': point.longitude,
                'leg': current_leg,
                'name': point.name,
                'type': station_type
            }

            station_query = Station.objects.filter(name=point.name)

            operation = None
            if len(station_query) == 0:
                # Creates a new station and adds the basic information
                station = Station()
                station.name = point.name
                station.type = station_type
                operation = "inserted"
            else:
                station = station_query[0]
                if station.latitude != point.latitude or station.longitude != point.longitude or station.leg != current_leg:

                    operation = "updated"

                    # updates information (from the new or the existing one)
                    station.latitude = point.latitude
                    station.longitude = point.longitude
                    station.leg = current_leg

                else:
                    operation = "skipped"

            if operation is not None:
                station.save()

            if operation == "inserted":
                total_created+=1
                action_text = "created"
            elif operation == "updated":
                total_modified+=1
                action_text = "modified"
            elif operation == "skipped":
                total_skipped += 1
            else:
                assert False

            if operation == "inserted" or operation == "modified":
                reports.append("Action: {action_text} Waypoint name: {name} Latitude: {latitude} Longitude: {longitude}".format(action_text=action_text, **waypoint_information))

    return (total_created, total_modified, total_skipped, reports)
