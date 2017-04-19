from django.db.models import Q
from main.models import Event, EventAction

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

def action_finished(event_action_id, event_number):
    event_actions_instant = EventAction.objects.filter(
        Q(id=event_action_id) & Q(type="TINSTANT"))

    if len(event_actions_instant) > 0:
        return True

    event_actions = EventAction.objects.filter(Q(event=event_number) & Q(type="TENDS"))

    if len(event_actions) > 0:
        # There is an TENDS event so it's finished
        return True

    return False


def event_not_opened(event_id):
    other_events = EventAction.objects.filter(Q(event_id=event_id))

    if len(other_events) == 0:
        return True
    else:
        return False


def open_event_numbers():
    """ Returns the event IDs that have been started and not finished. """
    started_not_finished = []
    event_actions = EventAction.objects.all()
    events = Event.objects.all()
    open_event_numbers_list = []

    # Adds events with TBEGNS and not finished
    for event_action in event_actions:
        if event_action.type == EventAction.tbegin():
            if not action_finished(event_action.id, event_action.event.number):
                open_event_numbers_list.append(event_action.event.number)

    for event in events:
        if event_not_opened(event.number):
            open_event_numbers_list.append(event.number)

    open_events_numbers_set = set(open_event_numbers_list)
    return list(open_events_numbers_set)