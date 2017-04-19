from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
from django.conf import settings
import datetime
from main import utils
import geojson

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

class Command(BaseCommand):
    help = 'Outputs the track on Geojson format. See the settings for the frequency'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        geojson_track = GeoJsonTrack()
        geojson_track.run()


class GeoJsonTrack:
    def __init__(self):
        pass

    def run(self):
        time_delta = datetime.timedelta(seconds=settings.MAP_RESOLUTION_SECONDS)

        first_date = GpggaGpsFix.objects.earliest().date_time
        last_date = GpggaGpsFix.objects.latest().date_time

        current_date = first_date

        locations = []
        while current_date < last_date:
            location = utils.ship_location(current_date)

            if location.latitude is not None and location.longitude is not None:
                locations.append((location.longitude, location.latitude))
                current_date = location.date_time + time_delta
            else:
                current_date = current_date + time_delta

        track = geojson.LineString(locations)

        file = open(settings.TRACK_MAP_FILEPATH, "w")
        geojson.dump(track, file)
