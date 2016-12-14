from django.conf import settings
import main.models

def can_user_change_events(path, user):
    # To make sure that the user can edit events
    if path.endswith("/add/"):
        return True

    # But if it's not /add/, if the user is in the "Add Events"
    # should not be able to change them
    for permission in main.models.cannot_change_events_all:
        if not user.has_perm(permission[0][0]):
            return False

    return True
