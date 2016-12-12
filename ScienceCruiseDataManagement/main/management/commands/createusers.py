from django.core.management.base import BaseCommand, CommandError
from main.models import Person
import django.contrib

class Command(BaseCommand):
    help = 'Creates admin users based on the Person table'

    def create_event_group(self):
        group = django.contrib.auth.models.Group.objects.create(name="Add events")
        return group

    def create_users(self, group):
        users = Person.objects.all()

        for user in users:
            login = "{} {}".format(user.name_first, user.name_last)
            created_user = django.contrib.auth.models.User.objects.create_user(login, password=login)
            created_user.is_staff = True
            created_user.groups.add(group)
            created_user.save()

            print("Created: {}".format(login))

    def handle(self, *args, **options):
        group = self.create_event_group()
        self.create_users(group)
