from django.core.management.base import BaseCommand, CommandError
from main.models import Person
from django.contrib.auth.models import User, Group, Permission

class Command(BaseCommand):
    help = 'Creates admin users based on the Person table'

    def add_arguments(self, parser):
        parser.add_argument('--createusers',
                            action='store_true',
                            dest='createusers',
                            default=False,
                            help="Creates the Django users from the Person table")

    def get_or_create_event_group(self):
        groups = Group.objects.filter(name="Add events")

        if len(groups) != 0:
            groups[0].delete()

        group = Group.objects.create(name="Add events")

        permissions = ["Can add event", "Can add event action", "Can add event report"]
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
