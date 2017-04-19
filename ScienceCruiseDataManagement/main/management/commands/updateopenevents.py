from django.core.management.base import BaseCommand, CommandError

from main import utils_event
from main.models import Event, EventAction, OpenEvent
from django.db import transaction

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
    help = 'Updates the table of open events. It should not be needed in normal operation'

    @transaction.atomic()
    def handle(self, *args, **options):
        event_numbers = utils_event.open_event_numbers()
        print(event_numbers)
        OpenEvent.objects.all().delete()

        for event_number in event_numbers:
            open_event = OpenEvent(number=event_number)
            open_event.save()
