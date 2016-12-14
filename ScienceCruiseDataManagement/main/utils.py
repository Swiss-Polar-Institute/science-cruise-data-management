from django.conf import settings
import main.models

def can_user_change_events(path, user):
    # To make sure that the user can edit events
    if path.endswith("/add/"):
        return True

    permission = main.models.cannot_change_events[0][0]

    # But if it's not /add/, if the user is in the "Add Events"
    # should not be able to change them
    if not user.has_perm(permission):
        return False

    return True
