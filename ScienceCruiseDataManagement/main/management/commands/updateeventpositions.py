from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction
from django.conf import settings

from main import utils

class Command(BaseCommand):
    help = 'Updates positions of latitude longitude of Event Actions'

    def add_arguments(self, parser):
        parser.add_argument('action', help="[update|dry-run]", type=str)

    def handle(self, *args, **options):
        if options['action'] == "dry-run":
            self.dry_run()

    def dry_run(self):
        event_actions = EventAction.objects.all().order_by('time')

        for event_action in event_actions:
            to_be_updated = False

            if event_action.latitude is None and event_action.longitude is None:
                if event_action.event.station is None or \
                                event_action.event.station in settings.UPDATE_LOCATION_STATIONS_TYPES:
                    Command.update(event_action)

    @staticmethod
    def update(event_action):
        location = utils.ship_position(event_action.time)
        if location[0] is not None and location[1] is not None:
            print("Should update event_action: {}\t{} {:.4f} {:.4f}".format(event_action.id, event_action.time, location[0], location[1]))
            # TODO: update it! (we want to verify something on the map before doing it)
        else:
            print("Missing information for event action ID: {} Time: {}".format(event_action.id, event_action.time))
