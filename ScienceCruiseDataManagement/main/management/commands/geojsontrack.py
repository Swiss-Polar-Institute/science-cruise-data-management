from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
from django.conf import settings
import datetime
from main import utils
import geojson


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

            current_date = current_date + time_delta

            print(current_date)

        track = geojson.LineString(locations)

        file = open(settings.TRACK_MAP_FILEPATH, "w")
        geojson.dump(track, file)
