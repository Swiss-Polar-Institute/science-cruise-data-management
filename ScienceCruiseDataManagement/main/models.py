from django.db import models
from django.db.models import Max
from django.utils import timezone

def next_event_number():
    latest = Event.objects.all().aggregate(Max('event_number'))

    if latest['user_id__max'] == None:
        return 1
    else:
        return latest["user_id__max"] + 1

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

def next_position_number():
    latest = Position.objects.all().aggregate(Max('number'))

    if latest['number__max'] == None:
        return 1
    else:
        return latest["number__max"] + 1

class PositionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)


class Position(models.Model):
    number = models.IntegerField(default=next_position_number, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    text = models.CharField(max_length=255, blank=True, null=True)
    position_type = models.ForeignKey(PositionType)

    def save(self, *args, **kwargs):
        if self.number is None:
            self.number = next_position_number()

        if self.text is None:
            self.text = ""

        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return "{}-{}-{}-({}, {})".format(self.id, self.number, self.text, self.latitude, self.longitude)