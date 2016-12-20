from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from smart_selects.db_fields import ChainedManyToManyField

cannot_change_events = (("cannot_change_events_special", "Cannot change events (special)"),)
cannot_change_events_action = (("cannot_change_events_action_special", "Cannot change events action (special)"),)

cannot_change_events_all = [cannot_change_events, cannot_change_events_action]


def next_event_number():
    latest = Event.objects.all().aggregate(Max('number'))

    if latest['number__max'] == None:
        return 1
    else:
        return latest["number__max"] + 1


class FilesStorage(models.Model):
    relative_path=models.CharField(max_length=255)
    kilobytes = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.relative_path, self.kilobytes)


class FilesStorageGeneral(models.Model):
    used = models.BigIntegerField()
    free = models.BigIntegerField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}-{}".format(self.used, self.free)


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name_plural="Countries"


class DeviceType(models.Model):
    url = models.CharField(max_length=255, null=True, blank=True, help_text = "If adding a new device leave this field blank.")
    code = models.CharField(max_length=255, unique=True, null=True, blank=True, help_text = "If adding a new device leave this field blank.")
    name = models.CharField(max_length=255, help_text = "Use a descriptive but short name for the device.")
    definition = models.TextField(help_text = "Give a full description of the device, including it's make, model, how it is used and a URL describing the device where possible.")
    version = models.CharField(max_length=255, null=True, blank=True, help_text = "If adding a new device leave this field blank.")
    deprecated = models.CharField(max_length=255, null=True, blank=True, help_text = "If adding a new device leave this field blank.")
    date = models.DateTimeField(null=True, blank=True, help_text = "If adding a new device leave this field blank.")
    source = models.CharField(choices = settings.VOCAB_SOURCES, default = settings.DEVICE_SOURCE_DEFAULT, max_length=255, help_text = "Use the default or speak to the data management team if generated for ACE does not apply.")

    def __str__(self):
        return "{}".format(self.name)


class ParentDevice(models.Model):
    name = models.CharField(max_length=255, unique=True)
    definition = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)


class ChildDevice(models.Model):
    # The name is "type_of_device" because if it's type the Form doesn't work
    # correctly (reserved word in Python)
    type_of_device = models.ForeignKey(DeviceType, verbose_name="Type")
    serial_number = models.CharField(max_length=255, unique=True)
    possible_parents = models.ManyToManyField(ParentDevice)

    def __str__(self):
        return "{}-{}".format(self.type_of_device.name, self.serial_number)

    class Meta:
        unique_together = (('type_of_device', 'serial_number'))


class PositionUncertainty(models.Model):
    code = models.CharField(max_length=255, unique=True)
    table_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(max_length=255, choices=settings.VOCAB_SOURCES, default=settings.UNCERTAINTY_DEFAULT)

    def __str__(self):
        return "{}-{}".format(self.code, self.name)

    class Meta:
        verbose_name_plural = "Position uncertainties"


class TimeUncertainty(models.Model):
    table_code = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    source = models.CharField(choices=settings.VOCAB_SOURCES, default=settings.UNCERTAINTY_DEFAULT, max_length=255)

    def __str__(self):
        return "{}".format(self.name)


    class Meta:
        verbose_name_plural = "Time uncertainties"


class Port(models.Model):
    url = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    country = models.ForeignKey(Country)
    latitude = models.FloatField()
    longitude = models.FloatField()
    version = models.CharField(max_length=255, null=True, blank=True)
    deprecated = models.CharField(max_length=255, null=True, blank=True)
    date = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, choices = settings.VOCAB_SOURCES)

    def __str__(self):
        return "{}".format(self.name)


class Leg(models.Model):
    number = models.IntegerField(unique=True)
    start_time = models.DateTimeField()
    start_port = models.ForeignKey(Port, related_name='start_port')

    end_time = models.DateTimeField(blank=True, null=True)
    end_port = models.ForeignKey(Port, related_name='end_port')

    @staticmethod
    def current_active_leg():
        legs = Leg.objects.all().order_by('start_time')

        for leg in legs:
            if leg.start_time > timezone.now() and (leg.end_time > timezone.now() or leg.end_time == None):
                return leg

        # Returns the last leg
        return leg

    def __str__(self):
        return "{}".format(self.number)


class Storage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.name)


class Preservation(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.name)


class SpeciesClassification(models.Model):
    phylum = models.CharField(max_length=255)
    class2 = models.CharField('Class', db_column='class', max_length=255)
    order = models.CharField(max_length=255)
    family = models.CharField(max_length=255)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}-{}-{}-{}-{}".format(
            self.species, self.genus, self.family, self.order, self.class2, self.phylum)

    class Meta:
        verbose_name_plural="Species classification"
        unique_together= (('phylum', 'class2', 'order', 'family', 'genus', 'species'),)


class SampleContent(models.Model):
    type = models.CharField(max_length=255, unique=True)
    species_classification = models.ForeignKey(SpeciesClassification)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.type)

class Organisation(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, null=True)

    def __str__(self):
        return "{}".format(self.name)


class PlatformType(models.Model):
    url =models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    definition = models.CharField(max_length=255)
    version = models.CharField(max_length=255, null=True, blank=True)
    deprecated = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, choices=settings.VOCAB_SOURCES)

    def __str__(self):
        return "{}".format(self.name)

class Platform(models.Model):
    url = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    country = models.ForeignKey(Country)
    platformtype = models.ForeignKey(PlatformType)
    source = models.CharField(max_length=255, choices=settings.VOCAB_SOURCES)

    def __str__(self):
        return "{}".format(self.name)


class Ship(models.Model):
    name = models.ForeignKey(Platform)
    imo = models.CharField(max_length=255, null=True, blank=True)
    callsign = models.CharField(max_length=255, null=True, blank=True)
    length = models.CharField(max_length=255, null=True, blank=True)
    breadth = models.CharField(max_length=255, null=True, blank=True)
    power = models.CharField(max_length=255, null=True, blank=True)
    gross_weight = models.CharField(max_length=255, null=True, blank=True)
    noise_design = models.CharField(max_length=255, null=True, blank=True)
    noise = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, choices=settings.VOCAB_SOURCES)

    def __str__(self):
        return "{}".format(self.name)


class Person(models.Model):
    title_choices = (("Mr", "Mr."),
                     ("Ms", "Ms."),
                     ("Miss", "Miss"),
                     ("Mrs", "Mrs."),
                     ("Dr", "Dr."),
                     ("Prof", "Prof."))

    name_title = models.CharField(choices=title_choices, max_length=255, null=True, blank=True)
    name_first = models.CharField(max_length=255)
    name_middle = models.CharField(max_length=255, blank=True, null=True)
    name_last = models.CharField(max_length=255)
    initials = models.CharField(max_length=5, unique=True)
    project = models.ManyToManyField('Project')
    organisation = models.ManyToManyField(Organisation)

    def __str__(self):
        return "{} {}".format(self.name_first, self.name_last)

    class Meta:
        verbose_name_plural="People"
        unique_together = (('name_first', 'name_last'),)


class Project(models.Model):
    number = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, unique=True)
    alternative_title = models.CharField(null=True, blank=True, max_length=255)
    principal_investigator = models.ForeignKey(Person, related_name="Principal_investigator", null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.title)


class StationType(models.Model):
    type = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.type)


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.ForeignKey(StationType)
    latitude = models.FloatField()
    longitude = models.FloatField()
    leg = models.ForeignKey(Leg)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    time_source = models.ForeignKey(ChildDevice, related_name='station_device_time_source', null=True, blank=True)
    time_uncertainty = models.ForeignKey(TimeUncertainty, null=True, blank=True)
    position_source = models.ForeignKey(ChildDevice, related_name='station_position_time_source', null=True, blank=True)
    position_uncertainty = models.ForeignKey(PositionUncertainty, null=True,blank=True)
    water_depth = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class Sample(models.Model):
    code = models.CharField(max_length=255, unique=True)
    event = models.ForeignKey('Event')
    storage = models.ForeignKey(Storage)
    preservation = models.ForeignKey(Preservation)
    owner = models.ForeignKey(Person)
    contents = models.ForeignKey(SampleContent)
    destination = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.code)


class Data(models.Model):
    event = models.ForeignKey('Event', related_name="Event01")
    project = models.ForeignKey(Project)
    storage_location = models.CharField(max_length=255)
    checked = models.BooleanField()


class Event(models.Model):
    parent_device = models.ForeignKey(ParentDevice, related_name="parent_device_event")
    child_devices = ChainedManyToManyField(
        ChildDevice,
        chained_field='parent_device',
        chained_model_field='possible_parents',
    )
    #    models.ManyToManyField(ChildDevice)
    station = models.ForeignKey(Station, null=True)

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        permissions = cannot_change_events

class EventReport(Event):
    class Meta:
        proxy = True
        verbose_name_plural="Event report"


class EventActionDescription(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

class StorageCrate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)


class EventAction(models.Model):
    event = models.ForeignKey(Event)

    # If changing the order modify tbegin, tends and tinstant
    # Perhaps this could be done creating the tuple out of a dictionary
    # Also, do think what happens in the database with the existing records
    # (probably should be migrated, and it's not happening automatically)
    type_choices = (("TBEGNS", "Begins"),
                     ("TENDS", "Ends"),
                     ("TINSTANT", "Instant"))

    @staticmethod
    def tbegin():
        return EventAction.type_choices[0][0]

    @staticmethod
    def tends():
        return EventAction.type_choices[1][0]

    @staticmethod
    def tinstant():
        return EventAction.type_choices[2][0]

    @staticmethod
    def tbegin_text():
        return EventAction.type_choices[0][1]

    @staticmethod
    def tends_text():
        return EventAction.type_choices[1][1]

    @staticmethod
    def tinstant_text():
        return EventAction.type_choices[1][1]


    type = models.CharField(choices=type_choices, max_length=255)
    description = models.ForeignKey(EventActionDescription)

    time = models.DateTimeField()
    time_source = models.ForeignKey(ChildDevice, related_name='eventaction_device_time_source')
    time_uncertainty = models.ForeignKey(TimeUncertainty)

    latitude = models.FloatField()
    longitude = models.FloatField()
    position_source = models.ForeignKey(ChildDevice, related_name='eventaction_position_time_source')
    position_uncertainty = models.ForeignKey(PositionUncertainty)

    water_depth = models.FloatField(null=True, blank=True)
    general_comments = models.TextField(null=True, blank=True)
    data_source_comments = models.TextField(null=True, blank=True)

    def clean(self):
        event_id = self.event_id        # cleaned_data['event'] doesn't have this one
                                        # probably because the form filters it?
        event_action_type = self.type

        tbegin = EventAction.tbegin()
        tends = EventAction.tends()
        tinstant = EventAction.tinstant()

        tbegin_text = EventAction.tbegin_text()
        tends_text = EventAction.tends_text()
        tinstant_text = EventAction.tinstant_text()


        if len(EventAction.objects.all().filter
                       (Q(event_id=event_id) & (Q(type=tends) |
                                                    (Q(type=tinstant)))))>0:
            raise ValidationError("Cannot add any EventAction because the Event has a '{}' or '{}'".format(tends_text,
                                                                                                      tinstant_text))

        if event_action_type == tends:
            if len(EventAction.objects.all().filter
                       (Q(event_id=event_id) & (Q(type=tends) | (Q(type=tinstant)))))>0:
                raise ValidationError("Cannot add {} because this Event already had '{}' or '{}'".format(tends, tends_text, tinstant_text))
            if len(EventAction.objects.all().filter
                       (Q(event_id=event_id) & (Q(type=tbegin)))) == 0:
                raise ValidationError("Cannot add '{}' because '{}' doesn't exist".format(tends_text, tbegin_text))


    def __str__(self):
        return "{}".format(self.event.id)

    class Meta:
        permissions = cannot_change_events_action

class Message(models.Model):
    date_time = models.DateTimeField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return "{}".format(self.subject)

class NetworkHost(models.Model):
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    location = models.CharField(max_length=255, help_text="In which floor, laboratory, container is this device", blank=True, null=True)
    comment = models.TextField(blank=True, null=True)