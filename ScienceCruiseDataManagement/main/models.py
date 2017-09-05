from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from smart_selects.db_fields import ChainedManyToManyField
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
#import data_storage_management.models

cannot_change = (("cannot_change_special", "Cannot change (special)"),)

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

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
        verbose_name_plural = "Countries"


class Island(models.Model):
    name = models.CharField(max_length=255, unique=True)
    mid_lat = models.FloatField(null=True, blank=True)
    mid_lon = models.FloatField(null=True, blank=True)
    island_group = models.CharField(max_length=255, null=True, blank=True)

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
    source = models.CharField(choices=settings.VOCAB_SOURCES, default = settings.DEVICE_SOURCE_DEFAULT, max_length=255, help_text = "Use the default or speak to the data management team if generated for ACE does not apply.")

    def __str__(self):
        return "{} - {}".format(self.name, self.source)


class SamplingMethod(models.Model):
    name = models.CharField(max_length=255, unique=True)
    definition = models.CharField(max_length=1000, null=True, blank=True)
    directory = models.ManyToManyField('data_storage_management.Item', blank=True)
    validity = models.CharField(max_length=255, choices=settings.VALIDITY_OPTIONS)
    date_validity_changed = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.definition)


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
    table_code = models.CharField(max_length=255, blank=True)
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
    city = models.CharField(max_length=255, blank=True, null=True)
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
    short_name = models.CharField(max_length=255, null=True)    # TODO: make short_name unique after migration
    uuid = models.CharField(max_length=255, default=None,       # TODO: make uuid unique after migration
                            help_text="Used for the Metadata Record")
    country = models.ForeignKey(Country, null=True, blank=True)
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


class Role(models.Model):
    role = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.role)


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
    initials = models.CharField(max_length=5)
    organisation = models.ManyToManyField(Organisation)
    email_address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        organisations = self.organisation.all()
        organisation_names = []

        for organisation in organisations:
            organisation_names.append(organisation.name)

        organisation_str = ";".join(organisation_names)

        return "{} {} - {}".format(self.name_first, self.name_last, organisation_str)

    class Meta:
        verbose_name_plural="People"
        unique_together = (('name_first', 'name_last'),)


class PersonRole(models.Model):
    person = models.ForeignKey(Person)
    project = models.ForeignKey('Project', null=True, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True)
    principal_investigator = models.BooleanField(default=False)
    leg = models.ManyToManyField(Leg, blank=True)

    class Meta:
        verbose_name_plural="People Roles"
        unique_together = (('person', 'project', 'role'),)


class Email(models.Model):
    person = models.ForeignKey(Person)
    email_address = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=False)
    webmail_password = models.CharField(max_length=6)
    server_password = models.CharField(max_length=20)

    def __str__(self):
        return "{}".format(self.person)


class EmailOversizeNotified(models.Model):
    from_email = models.CharField(max_length=1024)
    to_email = models.ForeignKey(Email)
    date_string = models.CharField(max_length=255, help_text="Date as it comes from the IMAP header", null=True)
    size = models.IntegerField()
    subject = models.CharField(max_length=1024)
    imap_uuid = models.CharField(max_length=50)
    added = models.DateTimeField(default=timezone.now)


class Mission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=255)
    institution = models.ForeignKey(Organisation)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.acronym)


class Project(models.Model):
    number = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, unique=True)
    alternative_title = models.CharField(null=True, blank=True, max_length=255)
    principal_investigator = models.ForeignKey(Person, related_name="Principal_investigator", null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    sampling_methods = models.ManyToManyField(SamplingMethod)

    def __str__(self):
        return "{} - {}".format(self.number, self.title)


class Device(models.Model):
    # Table contains full details of instruments.
    full_name = models.CharField(max_length=255, help_text="Give the full name of the device, eg. Simrad EK80 echo sounder.")
    shortened_name = models.CharField(max_length=255, null=True, blank=True, help_text="A brief name by which the device is often known, eg. CTD.")
    description = models.TextField(help_text="Give a full description of the device which includes some information about what it is used for, how it can be used and any specific details that separate it from similar instruments. If you have a URL about the device, please include it here.")
    main_device_type = models.ManyToManyField(DeviceType, related_name='device_type', blank=True, help_text="Select one or more options of available, from this list of controlled vocabulary devices. If there is nothing suitable, do not select anything. Note that there are some very specific devices and other more general categories, all of which should be selected if they are correct.")
    instruments = models.ManyToManyField('metadata.Instrument', blank=True, help_text="Used to link with GCMD instruments.")


    def __str__(self):
        return "{}".format(self.full_name)


class SpecificDevice(models.Model):
    # The name is "type_of_device" because if it's type the Form doesn't work
    # correctly (reserved word in Python)
    type_choices = (("serial number", "serial number"), ("no identifying mark", "no identifying mark"), ("mark handwritten on", "mark handwritten on"))

    type_of_device = models.ForeignKey(Device, verbose_name="Type", help_text="Choose the type of device")
    full_name = models.CharField(max_length=255, null=True, blank=True, help_text="Full name of the device as it is known.")
    shortened_name = models.CharField(max_length=255, null=True, blank=True, help_text="Shortened name or acronym of the device by which it is known.")
    description = models.TextField(null=True, blank=True, help_text="Give a full description of the device which includes some information about what it is used for, how it can be used and any specific details that separate it from similar instruments. If you have a URL about the device, please include it here.")
    sampling_method = models.ForeignKey(SamplingMethod, related_name="sampling_method_device", null=True,blank=True, help_text="Link each device to a sampling method so that the data can be linked to events.")
    directory = models.ManyToManyField('data_storage_management.Item', blank=True)
    identifying_mark = models.CharField(max_length=255, null=True, blank=True, help_text="If the device has an identifying number (prefereably a serial number), entering it here. This mark should distinguish from another instrument of the same type.")
    type_of_identifying_mark = models.CharField(max_length=50, choices=type_choices, help_text="Choose the type of identifying mark on the instrument.")
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ManyToManyField('SpecificDevice', blank=True, help_text="If the device is deployed by attaching it to another instrument, then it has a parent: enter this device here. Some devices may have more than one parent device, for example if the parent device breaks and is swapped.")
    platform = models.ManyToManyField(Platform, related_name='possible_platform', help_text="Select one or more platforms from which the device was operated or deployed.")
    device_contact = models.ManyToManyField(Person, help_text="Select the person / people who operated or was responsible for the instrument at some point during the voyage. This does not have to be every user of the instrument, but the main operator(s) for each leg.")
    leg_used = models.ManyToManyField(Leg, help_text="Select the leg(s) on which the device was used.")
    project = models.ManyToManyField(Project, help_text="Select the templates which used the device or got samples / data from its deployments.")
    calibration_required = models.BooleanField(help_text="Select this box if this device should be calibrated.")
    calibration_documents = models.BooleanField(help_text="Select this box if this device should be calibrated and the calibration documents are in the data folder.")
    calibration_comments = models.CharField(max_length=255, null=True, blank=True)
    device_comments = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return "{} - {}".format(self.type_of_device.full_name, self.identifying_mark)

    class Meta:
        unique_together = (('type_of_device', 'identifying_mark'))


class StationType(models.Model):
    type = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.type)


class Station(models.Model):
    outcome_choices = (("Not yet happened", "Not yet happened"), ("Success", "Success"), ("Cancelled", "Cancelled"))

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
    outcome = models.CharField(max_length=20, choices=outcome_choices, help_text="Select the option that best describes the outcome of the event. If the event did not happen because of weather or a decision to not do it, it should be marked as invalid.", default="Success")

    def __str__(self):
        return "{}".format(self.name)

class ProposedStation(models.Model):
    type_choices = (("Marine", "Marine"), ("Terrestrial", "Terrestrial"))

    name = models.CharField(null=True, blank=True, max_length=100)
    type = models.CharField(choices=type_choices, max_length=20)
    latitude = models.FloatField()
    longitude= models.FloatField()
    comment = models.CharField(max_length=300)

    def __str__(self):
        return "{} - {}".format(self.name, self.comment)

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
    file = models.CharField(max_length=255, blank=True, null=True)
    specific_contents = models.CharField(max_length=255, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.expedition_sample_code)


class ImportedFile(models.Model):
    file_name = models.CharField(max_length=255)
    date_imported = models.DateTimeField()
    object_type = models.CharField(max_length=255, help_text="From where this was imported")

    def __str__(self):
        return"{}".format(self.file_name)

    class Meta:
        unique_together = (('file_name', 'object_type'))


@receiver(post_save, sender=Sample)
def update_expedition_sample_code(sender, instance, **kwargs):
    # It's done in the post_save because the sample_id can be part of the expedition_sample_code
    if instance.expedition_sample_code is None or instance.expedition_sample_code == '':
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
    sampling_method = models.ForeignKey(SamplingMethod, related_name="sampling_method_event", help_text="Choose the instrument or method used for sampling")
    specific_devices = ChainedManyToManyField(
        SpecificDevice,
        chained_field='linked_device',
        chained_model_field='possible_parents',
        blank=True,
        verbose_name="Attached devices",
        help_text="Choose any devices that are attached to your instrument"
    )
    #    models.ManyToManyField(SpecificDevice)
    station = models.ForeignKey(Station, null=True, blank=True, help_text="Only choose a station name where the ship has stopped")
    data = models.BooleanField(help_text="Tick this box if raw data will be produced DURING this event (not after post-cruise processing).")
    samples = models.BooleanField(help_text="Tick this box if samples will be collected during this event.")
    outcome = models.CharField(max_length=20, choices=type_choices, help_text="Select the option that best describes the outcome of the station. If the event did not happen because of weather or a decision to not do it, it should be marked as invalid.", default="Not yet happened")
    imported_from_file = models.ForeignKey(ImportedFile, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.number)

    def save(self, *args, **kwargs):
        # Event without event action: it's opened
        previous_id = self.number
        super(Event, self).save(*args, **kwargs)

        if previous_id is None:
            # It's a new object, update OpenEvent table
            open_event = OpenEvent(number=self.number)
            open_event.save()

    class Meta:
        permissions = cannot_change


class EventReport(Event):
    class Meta:
        proxy = True
        verbose_name_plural = "Event report"


class OpenEvent(models.Model):
    number = models.IntegerField(unique=True, help_text="Event number that is opened", primary_key=True)


class EventActionDescription(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)


class EventsConsistencyV2(models.Model):
    choice_types = (("CTD", "CTD"),
                    ("UW", "UW"))

    type = models.CharField(max_length=255, choices=choice_types)
    event_from_project_code = models.IntegerField()
    event_from_expedition_code = models.ForeignKey(Event, related_name="Event_02")
    project = models.ForeignKey(Project)
    sample = models.ForeignKey(Sample)

    def __str__(self):
        return "Type: {} event from project code: {} event from expedition code: {} project: {} sample: {}".format(
                        self.type, self.event_from_project_code, self.event_from_expedition_code,
                        self.project, self.sample)


class EventsConsistency(models.Model):
    choice_types = (("CTD", "CTD"),
                    ("UW", "UW"))

    type = models.CharField(max_length=255, choices=choice_types)
    thing = models.CharField(max_length=255)
    event_from_sample = models.ForeignKey(Event)
    project = models.ForeignKey(Project)
    samples = models.ManyToManyField(Sample)

    def __str__(self):
        return "Project thing: {} Event: {} Project number: {} Type: {}".format(self.thing,
                                                                         self.event_from_sample,
                                                                         self.project.number,
                                                                         self.type)

    class Meta:
        unique_together = (('event_from_sample', 'project', 'type', 'thing'),)


class CtdCast(models.Model):
    ctd_cast_number = models.IntegerField()
    event_number = models.OneToOneField(Event)
    leg_number = models.ForeignKey(Leg)
    ctd_operator = models.ForeignKey(Person, null=True, blank=True)
    ctd_file_name = models.CharField(max_length=255, null=True, blank=True)
    ice_coverage = models.CharField(max_length=255, null=True, blank=True)
    sea_state = models.CharField(max_length=255, null=True, blank=True)
    water_depth = models.FloatField(null=True, blank=True)
    surface_temperature = models.FloatField(null=True, blank=True)
    surface_salinity = models.FloatField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.ctd_cast_number)

    class Meta:
        unique_together= (('ctd_cast_number', 'leg_number'),)
        verbose_name_plural = "CTD casts"


class TmrCast(models.Model):
    tmr_cast_number = models.IntegerField()
    event_number = models.OneToOneField(Event)
    leg_number = models.ForeignKey(Leg)

    def __str__(self):
        return "{}".format(self.tmr_cast_number)

    class Meta:
        unique_together = (('tmr_cast_number', 'leg_number'),)


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

    @staticmethod
    def text_to_type(text):
        if text == EventAction.tbegin_text():
            return EventAction.tbegin()
        elif text == EventAction.tends_text():
            return EventAction.tends()
        elif text == EventAction.tinstant_text():
            return EventAction.tinstant()
        else:
            print("Text was:", text)
            assert False

    type = models.CharField(choices=type_choices, max_length=255, help_text="Select the description of the time that you are entering", verbose_name= "Time description")
    description = models.ForeignKey(EventActionDescription, verbose_name="Description of event action", help_text="Select the description that describes the event action")

    time = models.DateTimeField(default=timezone.now, help_text="TIME IN UTC", verbose_name="Time of event action (UTC)")
    time_source = models.ForeignKey(TimeSource)
    time_uncertainty = models.ForeignKey(TimeUncertainty)

    latitude = models.FloatField(null=True, blank=True, help_text="Format: decimal degrees, i.e. -63.334. Note that south is negative. Only enter position for terrestrial work. Events at sea will automatically get their position from the ship's GPS.")
    longitude = models.FloatField(null=True, blank=True, help_text="Format: decimal degrees, i.e. -145.54. Note that west is negative. Only enter position for terrestrial work. Events at sea will automatically get their position from the ship's GPS.")
    position_source = models.ForeignKey(PositionSource, null=True, blank=True, help_text="Only enter position for terrestrial work. Events at sea will automatically get their position from the ship's GPS.")
    position_uncertainty = models.ForeignKey(PositionUncertainty, null=True, blank=True, help_text="Only enter position for terrestrial work. Events at sea will automatically get their position from the ship's GPS.")

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

        if self.id is not None:
            old_time = EventAction.objects.get(id=self.id).time
            if self.position_depends_on_time(force_update=True) and old_time != self.time:
                # It will get updated by the script updateeventlocations.py
                self.latitude = None
                self.longitude = None

        check_type = True
        if self.id is not None:
            # We are changing an existing event action...

            # Do not check the type. It allows invalid states (e.g. events with two begins, etc.)
            # because
            check_type = False
            # old_event_action = EventAction.objects.get(id=self.id)
            #
            # # ...if the type hasn't changed we don't need to check it.
            # # This simplifies the logic of the checks to not need to check for ourselves.
            # if self.type != old_event_action.type:
            #     check_type = False

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

            if event_action_type == tbegin and \
                len(EventAction.objects.filter(Q(event_id=event_id) & (Q(type=tbegin)))) > 0:
                raise ValidationError("Cannot add '{}' because this Event already had a '{}'".format(tbegin_text, tbegin_text))

        if event_action_type == tends:
            # Here if the type is tends() it has a start for sure or the validation
            # would have already failed
            event_begins = EventAction.objects.filter(Q(event_id=event_id) & Q(type=tbegin))
            for event_begin in event_begins:
                if self.time < event_begin.time:
                    raise ValidationError({
                        'time':"Time in the ends EventAction (this one) can't be earlier than the already entered begin's EventAction"
                    })

    def save(self, *args, **kwargs):
        super(EventAction, self).save(*args, **kwargs)

        if self.type == EventAction.tends() or self.type == EventAction.tinstant():
            # The event could be closed: in case that the user is changing an existing event.
            open_events = OpenEvent.objects.filter(number=self.event_id)

            if open_events.exists():
                open_events[0].delete()

        elif self.type == EventAction.tbegin():
            # If the event is not open: creates an open event (it could have been opened
            # if it was already tbegin())
            event_is_open = OpenEvent.objects.filter(number=self.event_id).exists()

            if not event_is_open:
                open_event = OpenEvent(number=self.event_id)
                open_event.save()
        else:
            assert False

    def delete(self, using=None, keep_parents=False):
        type = self.type
        event_id = self.event_id

        super(EventAction, self).delete(using=using, keep_parents=keep_parents)

        if type == self.tends() or type == self.tinstant():
            open_events = OpenEvent.objects.filter(number=self.event_id)
            if not open_events.exists():
                open_event = OpenEvent()
                open_event.number = event_id
                open_event.save()

    def __str__(self):
        return "{}".format(self.event.number)

    class Meta:
        permissions = cannot_change

    def position_depends_on_time(self, force_update=False):
        if self.type == EventAction.tends() and self.event.sampling_method.name in settings.UPDATE_LOCATION_POSITION_EXCEPTION_EVENT_ACTION_TYPE_ENDS_EXCEPTIONS:
            return False

        to_be_updated = (self.latitude is None and self.longitude is None) or force_update == True

        if to_be_updated:
            if self.event.station is None or \
                            self.event.station.type.type in settings.UPDATE_LOCATION_STATIONS_TYPES:
                return True

        return False


@receiver(post_delete, sender=EventAction)
def delete_event_action(sender, instance, **kwargs):
    if instance.type == EventAction.tends() or instance.type == EventAction.tinstant:
        event_is_open = OpenEvent.objects.filter(number=instance.event_id).exists()

        if not event_is_open:
            open_event = OpenEvent(number=instance.event_id)
            open_event.save()


class Message(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    person = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.subject)


class Depth(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    depth = models.FloatField()

    class Meta:
        get_latest_by = "date_time"

    def __str__(self):
        return "{}-{}".format(self.date_time, self.depth)


class NetworkHost(models.Model):
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    location = models.CharField(max_length=255, help_text="In which floor, laboratory, container is this device", blank=True, null=True)
    comment = models.TextField(blank=True, null=True)


class TimeChange(models.Model):
    date_changed_utc = models.DateField(unique=True)
    difference_to_utc_after_change = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.date_changed_utc)


class ContactDetails(models.Model):
    name = models.ForeignKey(Person)
    email = models.CharField(max_length=255, null=True, blank=True)
    other = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Contact details"

class MeasurelandQualifierFlags(models.Model):
    DEFAULT_PK = 1

    concept_id = models.CharField(max_length=255)
    preferred_label = models.CharField(max_length=255)
    alt_label = models.CharField(max_length=255)
    definition = models.TextField(null=True, blank=True)
    modified = models.DateTimeField()
    source = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.preferred_label)

    class Meta:
        verbose_name_plural = "Measureland Qualifier Flags"