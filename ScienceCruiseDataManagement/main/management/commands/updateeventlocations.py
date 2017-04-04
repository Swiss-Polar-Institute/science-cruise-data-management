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
        self._force_update = False

    def add_arguments(self, parser):
        parser.add_argument('action', help="[update|dry-run|force-update]", type=str)

    def handle(self, *args, **options):
        if options['action'] == "dry-run":
            self._dry_run = True
        elif options['action'] == "update" or options['action'] == "force-update":
            self._dry_run = False
            self._force_update = (options['action'] == "force-update")
        else:
            print("Unknown action, should be dry-run, update or force-update")
            exit(1)

        self._update_locations()

    def _update_locations(self):
        event_actions = EventAction.objects.order_by('time')

        for event_action in event_actions:
            if event_action.position_depends_on_time(self._force_update):
                self._update(event_action)

    def _update(self, event_action):
        ship_location = utils.ship_location(event_action.time)
        action_text_before=""

        if ship_location.latitude is not None and ship_location.longitude is not None:
            if self._dry_run:
                action_text = "Should update"
            else:
                action_text_before = "(Previously: Latitude: {} Longitude: {})".format(event_action.latitude, event_action.longitude)
                if event_action.latitude == float("{:.4f}".format(ship_location.latitude)) and event_action.longitude == float("{:.4f}".format(ship_location.longitude)):
                    print("Was going to update {} but it's the same than before, skips".format(event_action))
                    return

                event_action.latitude = "{:.4f}".format(ship_location.latitude)
                event_action.longitude = "{:.4f}".format(ship_location.longitude)
                event_action.position_source = self._position_source()
                event_action.position_uncertainty = self._position_uncertainty()

                action_text = "Updated"
                event_action.save()

            print("{} event_action: {}\t{} {:.4f} {:.4f} {}".format(action_text, event_action.id, event_action.time,
                                                                 ship_location.latitude, ship_location.longitude, action_text_before))

        elif not ship_location.is_valid:
            print("Event action {} location in the database is invalid. Date time: {}".format(event_action.id, event_action.time))
            print("In the event action is: Latitude: {} Longitude: {}".format(event_action.latitude, event_action.longitude))
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