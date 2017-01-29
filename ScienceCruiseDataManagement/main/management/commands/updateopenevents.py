from django.core.management.base import BaseCommand, CommandError

from main import utils_event
from main.models import Event, EventAction, OpenEvent
from django.db import transaction


class Command(BaseCommand):
    help = 'Updates the table of open events. It should not be needed in normal operation'

    @transaction.atomic()
    def handle(self, *args, **options):
        event_numbers = utils_event.open_event_numbers()
        print(event_numbers)
        OpenEvent.objects.all().delete()

        for event_number in event_numbers:
            open_event = OpenEvent(number=event_number)
            open_event.save()
