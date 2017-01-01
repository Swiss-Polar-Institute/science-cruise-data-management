from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates positions of latitude longitude of Event Actions'

    def add_arguments(self, parser):
        parser.add_argument('action', help="[update|dry-run]", type=str)

    def handle(self, *args, **options):
        if options['action'] == "dry-run":
            self.dry_run()

    def dry_run(self):
        event_actions = EventAction.objects.all()

        for event_action in event_actions:
            to_be_updated = False

            if event_action.latitude is None and event_action.longitude is None:
                if event_action.event.station is None or \
                                event_action.event.station in settings.UPDATE_LOCATION_STATIONS_TYPES:
                    print("Should update this event action: {}".format(event_action))
