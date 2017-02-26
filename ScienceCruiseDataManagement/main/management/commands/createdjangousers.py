from django.core.management.base import BaseCommand, CommandError
from main.models import Person, Leg
import main.models
from django.contrib.auth.models import User, Group, Permission
from django.conf import settings
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Creates admin users based on the Person table'

    def add_arguments(self, parser):
        parser.add_argument('--createusers',
                            action='store_true',
                            dest='createusers',
                            default=False,
                            help="Creates the Django users from the Person table")
        parser.add_argument('--leg',
                            type=int,
                            help="Specifies the leg for the commands that accepts it, e.g. printemails")

    def get_or_create_event_group(self):
        # Deletes it to from main.models import models a clean start
        if Group.objects.filter(name=settings.ADD_EVENTS_GROUP).exists():
            return Group.objects.filter(name=settings.ADD_EVENTS_GROUP)[0]

        assert False
        group = Group.objects.create(name=settings.ADD_EVENTS_GROUP)

        permissions = ["Can add event", "Can add event action", "Can add event report",
                       "Can change event", "Can change event report", "Can change event action"]

        models = main.models

        for permission in main.models.add_events:
            permissions.append(permission[0][1])

        print("Permissions:" , permissions)
        for permission in permissions:
            object_permission = Permission.objects.get(name=permission)
            group.permissions.add(object_permission)

        group.save()
        return group

    def create_users(self, group, leg_number):
        wanted_leg = Leg.objects.get(number=leg_number)
        users = Person.objects.all().filter(leg=wanted_leg).order_by("name_first")

        for user in users:
            login = "{} {}".format(user.name_first, user.name_last)
            users = User.objects.filter(username=login)

            if len(users) > 0:
                users[0].delete()

            # Logins should not have spaces. The admin pane doesn't allow them
            # but using create_user it allowed it (!)
            login = login.replace(" ", "")

            try:
                created_user = User.objects.create_user(username=login, password=login)
            except IntegrityError:
                print("This user already existed: {}".format(login))
                continue

            created_user.is_staff = True
            created_user.groups.add(group)
            created_user.save()

            print("Created: {}".format(login))

    def handle(self, *args, **options):
        if options['createusers']:
            group = self.get_or_create_event_group()
            self.create_users(group, leg_number=options['leg'])

        #group = self.create_event_group()
        #self.create_users(group)
