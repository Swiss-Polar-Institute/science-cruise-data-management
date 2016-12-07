from django.db import models
from django.db.models import Max
from django.utils import timezone

def next_event_number():
    latest = Event.objects.all().aggregate(Max('event_number'))

    return latest.get("event_number__max", 0) + 1

# Create your models here.
class Event(models.Model):

    latitude = models.FloatField()
    longitude = models.FloatField()
    event_number = models.IntegerField(default=next_event_number, unique=True)
    time = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return "{}".format(self.id)

class Project(models.Model):
    name=models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)