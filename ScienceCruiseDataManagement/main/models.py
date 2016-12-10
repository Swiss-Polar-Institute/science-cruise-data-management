from django.db import models
from django.db.models import Max
from django.utils import timezone

def next_event_number():
    latest = Event.objects.all().aggregate(Max('number'))

    if latest['number__max'] == None:
        return 1
    else:
        return latest["number__max"] + 1

# Create your models here.
#class Event(models.Model):
    #
    #latitude = models.FloatField()
    #longitude = models.FloatField()
    #event_number = models.IntegerField(default=next_event_number, unique=True)
    #time = models.DateTimeField(default=timezone.now, null=True)
    #
        ##def __str__(self):
    #return "{}".format(self.id)

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural="Countries"

class Project(models.Model):
    name=models.CharField(max_length=255)
    country=models.ForeignKey(Country, null=True)

    def __str__(self):
        return "{}".format(self.name)

#class Instrument(models.Model):
#    name = models.CharField(max_length=255)
#
#    def __str__(self):
#        return "{}".format(self.name)
#

class Storage(models.Model):
    #instrument=models.ForeignKey(Instrument, null=True)
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
    number = models.IntegerField("Event number", help_text="User controlled ID", default=next_position_number, unique=True)
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


############################################### SERIOUS STUFF
class Instrument(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

class EventActionType(models.Model):
    code = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.code)


class PositionUncertainty(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    # TODO: change it
    list = models.CharField(max_length=255)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class TimeUncertainty(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    # TODO: change it
    list = models.CharField(max_length=255)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class Port(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)


class Leg(models.Model):
    name = models.CharField(max_length=255)
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    start_time = models.DateTimeField()
    start_port = models.ForeignKey(Port, related_name='start_port')

    end_latitude = models.FloatField()
    end_longitude = models.FloatField()
    end_time = models.DateTimeField()
    end_port = models.ForeignKey(Port, related_name='end_port')

    def __str__(self):
        return "{}".format(self.name)


class Event(models.Model):
    number = models.IntegerField(default=next_event_number, unique=True)
    leg = models.ForeignKey(Leg, default="")
    device = models.ForeignKey(Instrument)

    def __str__(self):
        return "{}".format(self.number)


class EventActionDescription(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class TimeSource(models.Model):
    name = models.CharField(max_length=255)

    # TODO: change list to something else
    list = models.CharField(max_length=255)

    code = models.CharField(max_length=255)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class PositionSource(models.Model):
    name = models.CharField(max_length=255)

    # TODO: change list to something else
    list = models.CharField(max_length=255)

    code = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class EventAction(models.Model):
    event = models.ForeignKey(Event)
    event_action_type = models.ForeignKey(EventActionType)
    event_action_description = models.ForeignKey(EventActionDescription)

    date_time = models.DateTimeField()
    time_source = models.ForeignKey(TimeSource)
    time_uncertainty = models.ForeignKey(TimeUncertainty)

    latitude = models.FloatField()
    longitude = models.FloatField()
    position_source = models.ForeignKey(PositionSource)
    position_uncertainty = models.ForeignKey(PositionUncertainty)

    water_depth = models.FloatField(null=True, blank=True)
    general_comments = models.TextField(null=True, blank=True)
    data_source_comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.event.number)