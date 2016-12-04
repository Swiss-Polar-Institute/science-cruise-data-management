from django.db import models
from django.db.models import Max


def next_event_number():
    latest = Event.objects.all().aggregate(Max('event_number'))

    if latest['event_number__max'] is None:
        return 1
    else:
        return latest['event_number__max'] + 1

# Create your models here.
class Event(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    event_number = models.IntegerField(default=next_event_number, unique=True)
    time = models.DateTimeField()

    def __str__(self):
        return "{}".format(self.id)

class Project(models.Model):
    name=models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)