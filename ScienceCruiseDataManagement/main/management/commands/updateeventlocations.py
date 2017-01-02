from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction, PositionUncertainty, PositionSource
from django.conf import settings

from main import utils

class Command(BaseCommand):
    help = 'Updates locations of latitude longitude of Event Actions'

    def __init__(self):
        self._dry_run = True
        self._position_source_object = None
        self._position_uncertainty_object = None

    def add_arguments(self, parser):
        parser.add_argument('action', help="[update|dry-run]", type=str)

    def handle(self, *args, **options):
        if options['action'] == "dry-run":
            self._dry_run = True
        elif options['action'] == "update":
            self._dry_run = False
        else:
            print("Unknown action, should be dry-run or update")
            exit(1)

        self._update_locations()

    def _update_locations(self):
        event_actions = EventAction.objects.all().order_by('time')

        for event_action in event_actions:
            if event_action.latitude is None and event_action.longitude is None:
                if event_action.event.station is None or \
                                event_action.event.station in settings.UPDATE_LOCATION_STATIONS_TYPES:
                    self._update(event_action)

    def _update(self, event_action):
        ship_location = utils.ship_location(event_action.time)

        if ship_location.latitude is not None and ship_location.longitude is not None:
            if self._dry_run:
                action_text = "Should update"
            else:
                event_action.latitude = ship_location.latitude
                event_action.longitude = ship_location.longitude
                event_action.position_source = self._position_source()
                event_action.position_uncertainty = self._position_uncertainty()

                action_text = "Updated"
                event_action.save()

            print("{} event_action: {}\t{} {:.4f} {:.4f}".format(action_text, event_action.id, event_action.time,
                                                                 ship_location.latitude, ship_location.longitude))

        else:
            print("Missing information for event action ID: {} Time: {}".format(event_action.id, event_action.time))

    def _position_uncertainty(self):
        if self._position_uncertainty_object is None:
            self._position_uncertainty_object = PositionUncertainty.objects.get(name=settings.UPDATE_LOCATION_POSITION_UNCERTAINTY_NAME)

        return self._position_uncertainty_object

    def _position_source(self):
        if self._position_source_object is None:
            self._position_source_object = PositionSource.objects.get(name=settings.UPDATE_LOCATION_POSITION_SOURCE_NAME)

        return self._position_source_object