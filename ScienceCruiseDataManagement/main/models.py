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

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

class Project(models.Model):
    name=models.CharField(max_length=255)
    country=models.ForeignKey(Country, null=True)

    def __str__(self):
        return "{}".format(self.name)

class Instrument(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

class Storage(models.Model):
    instrument=models.ForeignKey(Instrument, null=True)
    relative_path=models.CharField(max_length=255)
    kilobytes = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.instrument.name, self.kilobytes)

class General_Storage(models.Model):
    used = models.BigIntegerField()
    free = models.BigIntegerField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}-{}".format(self.used, self.free)

class Poi(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}-{}-({}, {})".format(self.id, self.text, self.latitude, self.longitude)