from django.core.management.base import BaseCommand, CommandError
from main.models import Person
import main.models
from django.contrib.auth.models import User, Group, Permission
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates admin users based on the Person table'

    def add_arguments(self, parser):
        parser.add_argument('--createusers',
                            action='store_true',
                            dest='createusers',
                            default=False,
                            help="Creates the Django users from the Person table")

    def get_or_create_event_group(self):
        # Deletes it to from main.models import modelse a clean start
        if Group.objects.filter(name=settings.ADD_EVENTS_GROUP).exists():
            Group.objects.filter(name=settings.ADD_EVENTS_GROUP).delete()

        group = Group.objects.create(name=settings.ADD_EVENTS_GROUP)

        permissions = ["Can add event", "Can add event action", "Can add event report",
                       "Can change event", "Can change event report", "Can change event action"]

        for permission in main.models.cannot_change_events_all:
            permissions.append(permission[0][1])

        print("Permissions:" , permissions)
        for permission in permissions:
            object_permission = Permission.objects.get(name=permission)
            group.permissions.add(object_permission)

        group.save()
        return group

    def create_users(self, group):
        users = Person.objects.all()

        for user in users:
            login = "{} {}".format(user.name_first, user.name_last)
            users = User.objects.filter(username=login)

            if len(users) > 0:
                users[0].delete()

            # Logins should not have spaces. The admin pane doesn't allow them
            # but using create_user it allowed it (!)
            login = login.replace(" ", "")

            created_user = User.objects.create_user(username=login, password=login)

            created_user.is_staff = True
            created_user.groups.add(group)
            created_user.save()

            print("Created: {}".format(login))

    def handle(self, *args, **options):
        if options['createusers']:
            group = self.get_or_create_event_group()
            self.create_users(group)

        #group = self.create_event_group()
        #self.create_users(group)
