from django.core.management.base import BaseCommand, CommandError
from main.models import EventAction

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
            if event_action.latitude is None and event_action.longitude is None and \
                event_action.event.station is None:
                print(event_action)