from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from smart_selects.db_fields import ChainedManyToManyField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

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

class Island(models.Model):
    name = models.CharField(max_length=255, unique=True)
    mid_lat = models.FloatField(null=True, blank=True)
    mid_lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)

class IslandLandings(models.Model):
    island = models.ForeignKey(Island)
    person = models.ForeignKey('Person')
    date = models.DateField()

    def __str__(self):
        return "{}-{}".format(self.island, self.person)

    class Meta:
        verbose_name_plural = "Island Landings"

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
    definition = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.definition)


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
        return "{}".format(self.name)

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

class TimeSource(models.Model):
    name = models.CharField(max_length=255, unique=True)
    definition = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.name, self.definition)

class PositionSource(models.Model):
    name = models.CharField(max_length=255, unique=True)
    definition = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.name, self.definition)


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
    start_time = models.DateTimeField(help_text="TIME IN UTC", verbose_name="Start time (UTC)")
    start_port = models.ForeignKey(Port, related_name='start_port')

    end_time = models.DateTimeField(blank=True, null=True, help_text="TIME IN UTC", verbose_name="End time (UTC)")
    end_port = models.ForeignKey(Port, related_name='end_port')

    @staticmethod
    def current_active_leg():
        legs = Leg.objects.all().order_by('start_time')

        for leg in legs:
            if leg.end_time == None and leg.start_time< timezone.now():
                return leg
            elif (leg.start_time < timezone.now() and (leg.end_time > timezone.now())):
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
    url = models.CharField(max_length=255, null=True, blank=True)
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
    platform_type = models.ForeignKey(PlatformType)
    source = models.CharField(max_length=255, choices=settings.VOCAB_SOURCES)

    def __str__(self):
        return "{}".format(self.name)


class Ship(models.Model):
    name = models.ForeignKey(Platform)
    shortened_name = models.CharField(max_length=255, unique=True)
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
    principal_investigator = models.BooleanField()
    leg = models.ManyToManyField(Leg, blank=True)

    def __str__(self):
        return "{} {}".format(self.name_first, self.name_last)

    class Meta:
        verbose_name_plural="People"
        unique_together = (('name_first', 'name_last'),)


class Mission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.acronym)


class Project(models.Model):
    number = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, unique=True)
    alternative_title = models.CharField(null=True, blank=True, max_length=255)
    principal_investigator = models.ForeignKey(Person, related_name="Principal_investigator", null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.number, self.title)


class StationType(models.Model):
    type = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.type)


class Station(models.Model):
    name = models.IntegerField(unique=True)
    type = models.ForeignKey(StationType)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    leg = models.ForeignKey(Leg)
    arrival_time = models.DateTimeField(null=True, blank=True, help_text="TIME IN UTC", verbose_name="Arrival time (UTC)")
    departure_time = models.DateTimeField(null=True, blank=True, help_text="TIME IN UTC",verbose_name="Departure time (UTC)")
    time_source = models.ForeignKey(TimeSource, related_name='station_device_time_source', null=True, blank=True)
    time_uncertainty = models.ForeignKey(TimeUncertainty, null=True, blank=True)
    position_source = models.ForeignKey(PositionSource, related_name='station_position_time_source', null=True, blank=True)
    position_uncertainty = models.ForeignKey(PositionUncertainty, null=True,blank=True)
    water_depth = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


def default_ship_id():
    platform = Platform.objects.get(name=settings.DEFAULT_PLATFORM_NAME)
    return Ship.objects.get(name=platform).id


def default_mission_id():
    return Mission.objects.get(name=settings.DEFAULT_MISSION_NAME).id


def current_active_leg_id():
    return Leg.current_active_leg().id


class Preservation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)


class Sample(models.Model):
    # It's updated by the function update_expedition_sample_code. But it's null for a moment while we get the
    # ID since the expedition_sample_code has the primary key of this table. So it needs to be stored
    # and then updated.
    expedition_sample_code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    project_sample_number = models.CharField(max_length=255, null=True, blank=True)
    contents = models.CharField(max_length=255)
    crate_number = models.CharField(max_length=255, null=True, blank=True)
    storage_type = models.CharField(max_length=255, null=True, blank=True)
    storage_location = models.CharField(max_length=255, null=True, blank=True)
    offloading_port = models.CharField(max_length=255)
    destination = models.CharField(max_length=255, null=True, blank=True)
    ship = models.ForeignKey(Ship, default=default_ship_id)
    mission = models.ForeignKey('Mission', default=default_mission_id)
    leg = models.ForeignKey('Leg', default=current_active_leg_id)
    project = models.ForeignKey('Project')
    julian_day = models.IntegerField()
    event = models.ForeignKey('Event')
    pi_initials = models.ForeignKey('Person')
    preservation = models.ForeignKey(Preservation, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.expedition_sample_code)


@receiver(post_save, sender=Sample)
def update_expedition_sample_code(sender, instance, **kwargs):
    # It's done in the post_save because the sample_id can be part of the expedition_sample_code
    if instance.expedition_sample_code is None:
        instance.expedition_sample_code = settings.EXPEDITION_SAMPLE_CODE(instance)
        instance.save()


class Data(models.Model):
    event = models.ForeignKey('Event', related_name="Event01")
    project = models.ForeignKey(Project)
    storage_location = models.CharField(max_length=255)
    checked = models.BooleanField()


class Event(models.Model):
    type_choices = (("Not yet happened", "Not yet happened"), ("Success", "Success"), ("Failure", "Failure"), ("Invalid", "Invalid"))

    number = models.AutoField(primary_key=True)
    parent_device = models.ForeignKey(ParentDevice, related_name="parent_device_event", verbose_name="Sampling method", help_text="Choose the instrument or method used for sampling")
    child_devices = ChainedManyToManyField(
        ChildDevice,
        chained_field='parent_device',
        chained_model_field='possible_parents',
        blank=True,
        verbose_name="Attached devices",
        help_text="Choose any devices that are attached to your instrument"
    )
    #    models.ManyToManyField(ChildDevice)
    station = models.ForeignKey(Station, null=True, blank=True, help_text="Only choose a station name where the ship has stopped")
    data = models.BooleanField(help_text="Tick this box if raw data will be produced DURING this event (not after post-cruise processing).")
    samples = models.BooleanField(help_text="Tick this box if samples will be collected during this event.")
    outcome = models.CharField(max_length=20, choices=type_choices, help_text="Select the option that best describes the outcome of the event. If the event did not happen because of weather or a decision to not do it, it should be marked as invalid.", default="Success")

    def __str__(self):
        return "{}".format(self.number)

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
    event = models.ForeignKey(Event, help_text="""Select the event from the list for which you want to enter an action.<br>
                                               If your event is not in the list check the event's outcome: should be success or failure. And check that the event hasn't been completed either<br>
                                               (e.g. it should not have an 'ends' or 'tinstant' event action")""")

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
        return EventAction.type_choices[2][1]

    type = models.CharField(choices=type_choices, max_length=255, help_text="Select the description of the time that you are entering", verbose_name= "Time description")
    description = models.ForeignKey(EventActionDescription, verbose_name="Description of event action", help_text="Select the description that describes the event action")

    time = models.DateTimeField(default=timezone.now, help_text="TIME IN UTC", verbose_name="Time of event action (UTC)")
    time_source = models.ForeignKey(TimeSource)
    time_uncertainty = models.ForeignKey(TimeUncertainty)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    position_source = models.ForeignKey(PositionSource, null=True, blank=True)
    position_uncertainty = models.ForeignKey(PositionUncertainty, null=True, blank=True)

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

        check_type = True
        if self.id is not None:
            # We are changing an existing event action...
            old_event_action = EventAction.objects.get(id=self.id)

            # ...if the type hasn't changed we don't need to check it.
            # This simplifies the logic of the checks to not need to check for ourselves.
            if self.type == old_event_action.type:
                check_type = False

        if check_type:
            if len(EventAction.objects.filter
                           (Q(event_id=event_id) & (Q(type=tends) |
                                                        (Q(type=tinstant)))))>0:
                raise ValidationError("Cannot add any EventAction because the Event has a '{}' or '{}'".format(tends_text,
                                                                                                          tinstant_text))

            if event_action_type == tends:
                if len(EventAction.objects.filter
                           (Q(event_id=event_id) & (Q(type=tends) | (Q(type=tinstant)))))>0:
                    raise ValidationError("Cannot add '{}' because this Event already had '{}' or '{}'".format(tends, tends_text, tinstant_text))
                if len(EventAction.objects.filter
                           (Q(event_id=event_id) & (Q(type=tbegin)))) == 0:
                    raise ValidationError("Cannot add '{}' because '{}' doesn't exist".format(tends_text, tbegin_text))

        if event_action_type == tends:
            # Here if the type is tends() it has a start for sure or the validation
            # would have already failed
            event_begin = EventAction.objects.get(Q(event_id=event_id) & Q(type=tbegin))
            if self.time < event_begin.time:
                raise ValidationError({
                    'time':"Time in the ends EventAction (this one) can't be earlier than the already entered begin's EventAction"
                })

    def __str__(self):
        return "{}".format(self.event.number)

    class Meta:
        permissions = cannot_change_events_action


class Message(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    person = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.subject)


class NetworkHost(models.Model):
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    location = models.CharField(max_length=255, help_text="In which floor, laboratory, container is this device", blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
