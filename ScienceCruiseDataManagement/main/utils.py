from django.conf import settings


def can_user_change_events(path, user):
    # To make sure that the user can edit events
    if path.endswith("/add/"):
        return True

    # But if it's not /add/, if the user is in the "Add Events"
    # should not be able to change them
    if user.groups.filter(name=settings.ADD_EVENTS_GROUP).exists():
        return False

    return True
