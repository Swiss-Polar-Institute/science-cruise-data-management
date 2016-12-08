from django.core.management.base import BaseCommand, CommandError
from main.models import Country

class Command(BaseCommand):
    help = 'Test adding a country'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        country = Country()
        country.name = options['name']
        country.save()
