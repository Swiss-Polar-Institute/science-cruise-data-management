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


class Storage(models.Model):
    #instrument=models.ForeignKey(Instrument, null=True)
    relative_path=models.CharField(max_length=255)
    kilobytes = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.instrument.name, self.kilobytes)

class General_Storage(models.Model):
    used = models.BigIntegerField()
    free = models.BigIntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}-{}".format(self.used, self.free)

def next_position_number():
    latest = Position.objects.all().aggregate(Max('number'))

    if latest['number__max'] == None:
        return 1
    else:
        return latest["number__max"] + 1

#class PositionType(models.Model):
#   name = models.CharField(max_length=255)
#
#   def __str__(self):
#       return "{}".format(self.name)


#class Position(models.Model):
#    number = models.IntegerField("Event number", help_text="User controlled ID", default=next_position_number, unique=True)
#    latitude = models.FloatField()
#    longitude = models.FloatField()
#    text = models.CharField(max_length=255, blank=True, null=True)
#    position_type = models.ForeignKey(PositionType)
#
#
#    def save(self, *args, **kwargs):
#        if self.number is None:
#            self.number = next_position_number()
#
#        if self.text is None:
#            self.text = ""
#
#        super(Position, self).save(*args, **kwargs)
#
#    def __str__(self):
#        return "{}-{}-{}-({}, {})".format(self.id, self.number, self.text, self.latitude, self.longitude)


############################################### SERIOUS STUFF
class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural="Countries"


class Device(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)


class PositionUncertainty(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    # TODO: change it
    list = models.CharField(max_length=255)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.code, self.name)


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
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return "{}".format(self.name)


class Leg(models.Model):
    number = models.IntegerField(unique=True)
    start_time = models.DateTimeField()
    start_port = models.ForeignKey(Port, related_name='start_port')

    end_time = models.DateTimeField(blank=True, null=True)
    end_port = models.ForeignKey(Port, related_name='end_port')

    def __str__(self):
        return "{}".format(self.number)


class Storage(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Preservation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class SpeciesClassification(models.Model):
    phylum = models.CharField(max_length=255)
    class2 = models.CharField('Class', db_column='class', max_length=255)
    order = models.CharField(max_length=255)
    family = models.CharField(max_length=255)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural="Species classification"


class SampleContent(models.Model):
    type = models.CharField(max_length=255)
    species_classification = models.ForeignKey(SpeciesClassification)
    description = models.TextField()

    def __str__(self):
        return "{}".format(type)

class Organisation(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country)

class Person(models.Model):
    title_choices = (("Mr", "Mr."),
                     ("Ms", "Ms."))

    name_title = models.CharField(choices=title_choices, max_length=255)
    name_first = models.CharField(max_length=255)
    name_middle = models.CharField(max_length=255, blank=True, null=True)
    name_last = models.CharField(max_length=255)
    project = models.ManyToManyField('Project', blank=True, null=True)
    organisation = models.ManyToManyField(Organisation)

    def __str__(self):
        return "{} {}".format(self.name_first, self.name_last)

    class Meta:
        verbose_name_plural="People"


class Project(models.Model):
    number = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    alternative_title = models.CharField(null=True, blank=True, max_length=255)
    principal_investigator = models.ForeignKey(Person, related_name="Principal_investigator")
    abstract = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.title)


class TimeSource(models.Model):
    name = models.CharField(max_length=255)

    # TODO: change list to something else
    list = models.CharField(max_length=255)

    code = models.CharField(max_length=255)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class PositionSource(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    # TODO: change list to something else
    list = models.CharField(max_length=255)

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class StationType(models.Model):
    type = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.type)


class Station(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(StationType)
    latitude = models.FloatField()
    longitude = models.FloatField()
    leg = models.ForeignKey(Leg)
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()
    time_source = models.ForeignKey(TimeSource)
    time_uncertainty = models.ForeignKey(TimeUncertainty)
    position_source = models.ForeignKey(PositionSource)
    position_uncertainty = models.ForeignKey(PositionUncertainty)
    water_depth = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

class Sample(models.Model):
    code = models.CharField(max_length=255)
    event = models.ForeignKey('Event')
    storage = models.ForeignKey(Storage)
    preservation = models.ForeignKey(Preservation)
    owner = models.ForeignKey(Person)
    contents = models.ForeignKey(SampleContent)
    destination = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(code)


class Data(models.Model):
    event = models.ForeignKey('Event', related_name="Event01")
    project = models.ForeignKey(Project)
    storage_location = models.CharField(max_length=255)
    checked = models.BooleanField()


class Event(models.Model):
    number = models.IntegerField(default=next_event_number, unique=True)
    device = models.ForeignKey(Device)
    station = models.ForeignKey(Station)
    # data = models.ManyToManyField(Data, related_name="Data01", blank=True)
    # samples = models.ManyToManyField(Sample, related_name="Sample01", blank=True)

    # def save(self, *args, **kwargs):
    #    ok = False
    #    try:
    #        a=self.data
    #        b=self.samples
    #        ok = True
    #    except ValueError:
    #        ok = False

    #    if ok:
    #        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.number)


class EventReport(Event):
    class Meta:
        proxy = True
        verbose_name_plural="Event report"


class EventActionDescription(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class StorageCrate(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

class EventAction(models.Model):
    event = models.ForeignKey(Event)

    type_choices = (("TBEGNS", "Begins"),
                     ("TENDS", "Ends"),
                     ("INSTANT", "Instant"))

    type = models.CharField(choices=type_choices, max_length=255)
    description = models.ForeignKey(EventActionDescription)

    time = models.DateTimeField()
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
