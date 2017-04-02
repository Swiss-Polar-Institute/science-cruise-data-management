from django.core.management.base import BaseCommand, CommandError
from ship_data.models import GpggaGpsFix
from django.conf import settings
import datetime
from main import utils
from main.models import SamplingMethod
import geojson
from ship_data.management.commands.qualitycheckgps import ship_location


class Command(BaseCommand):
    help = 'Outputs the track on Geojson format. For the passed GPS'

    def add_arguments(self, parser):
        parser.add_argument('gps_name', type=str, help="Sampling method (GPS name) to create the track for")

    def handle(self, *args, **options):
        gps = SamplingMethod.objects.get(name=options['gps_name'])

        geojson_track = GeoJsonTrack(gps)
        geojson_track.run()


class GeoJsonTrack:
    def __init__(self, gps):
        self._gps = gps

    def run(self):
        time_delta = datetime.timedelta(seconds=600)

        first_date = GpggaGpsFix.objects.filter(device=self._gps).earliest().date_time
        last_date = GpggaGpsFix.objects.filter(device=self._gps).latest().date_time

        current_date = first_date

        locations = []
        while current_date < last_date:
            location = ship_location(current_date, self._gps)

            if location is not None:
                locations.append((location.longitude, location.latitude))
                current_date = location.date_time + time_delta
            else:
                current_date = current_date + time_delta

        track = geojson.LineString(locations)

        file = open(self._gps.name + ".json", "w")
        geojson.dump(track, file)
