from django.db import models
from main.models import Person, DeviceType, Project, Leg, SpecificDevice
import django.utils.timezone
from django.core.exceptions import ValidationError
from django.db.models import Q

class HardDisk(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, null=True)
    person = models.ForeignKey(Person, null=True, blank=True)
    added_date_time = models.DateTimeField(default=django.utils.timezone.now)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.uuid)


class SharedResource(models.Model):
    ip = models.GenericIPAddressField()
    shared_resource = models.CharField(max_length=255)
    added_date_time = models.DateTimeField(default=django.utils.timezone.now)
    person = models.ForeignKey(Person, null=True, blank=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('ip', 'shared_resource'),)

    def __str__(self):
        return "//{}/{}".format(self.ip, self.shared_resource)


class NASResource(models.Model):
    shared_resource = models.CharField(max_length=255, unique=True)
    added_date_time = models.DateTimeField(default=django.utils.timezone.now)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.shared_resource)

    class Meta:
        verbose_name_plural = "NAS Directories"


class Item(models.Model):
    source_directory = models.CharField(max_length=255, null=True, blank=True, help_text="If it's a directory make sure that ends with / to avoid creating subdirectories. If it's a file(s) then make sure to not have it so it copies them")
    destination_directory = models.CharField(max_length=255, help_text="Can't start with /, it's a relative path")

    # A directory should come from only one of these sources
    hard_disk = models.ForeignKey(HardDisk, null=True, blank=True)
    shared_resource = models.ForeignKey(SharedResource, null=True, blank=True)
    nas_resource = models.ForeignKey(NASResource, null=True, blank=True)

    added_date_time  = models.DateTimeField(default=django.utils.timezone.now)

    source_instrument = models.ManyToManyField(SpecificDevice, blank=True, help_text="Select the instrument(s) which produced the data in this folder.")

    def __str__(self):
        if self.hard_disk is not None:
            return "HDD {} From: {} To: {}".format(self.hard_disk.uuid, self.source_directory, self.destination_directory)
        elif self.shared_resource is not None:
            return "\\{}\\{} From: {} To: {}".format(self.shared_resource.ip, self.shared_resource.shared_resource, self.source_directory, self.destination_directory)
        elif self.nas_resource is not None:
            return "NAS {} From: {} To: {}".format(self.nas_resource.shared_resource, self.source_directory, self.destination_directory)
        else:
            return ""

    def clean(self):
        directories_errors = {}
        if self.destination_directory.startswith("/"):
            directories_errors['destination_directory'] = "Destination directory cannot start with /"
        if not self.source_directory.startswith("/"):
            directories_errors['source_directory'] = "Source directory has to start with /"

        if len(directories_errors) > 0:
            raise ValidationError(directories_errors)

        same_destinations = Item.objects.filter(Q(destination_directory=self.destination_directory) &
                                                (~Q(hard_disk=self.hard_disk) | ~Q(shared_resource=self.shared_resource) | ~Q(nas_resource=self.nas_resource)))
        if same_destinations.exists():
            raise ValidationError("Can't add this directory because the same destination already exists from a different source")


class Directory(Item):
    class Meta:
        verbose_name_plural = "Directories"


class File(Item):
    pass


class ShipData(Item):
    def clean(self):
        """ This one is not used to copy data from places but only to document the instruments. So
        this avoids any validation that happens with other directories. """
        pass

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        verbose_name_plural = "Ship data"


class DirectoryImportLog(models.Model):
    directory = models.ForeignKey(Directory)
    updated_time = models.DateTimeField(default=django.utils.timezone.now)
    success = models.BooleanField()


class DataManagementProgress(models.Model):
    type_choices = (("Complete", "Complete"),
                    ("In progress", "In progress"),
                    ("Not started", "Not started"))

    project = models.ForeignKey(Project)
    leg = models.ForeignKey(Leg)
    event_recording = models.CharField(max_length=255, choices=type_choices)
    events_complete = models.BooleanField()
    sample_recording = models.CharField(max_length=255, choices=type_choices)
    samples_complete = models.BooleanField()
    metadata_record = models.CharField(max_length=255, choices=type_choices)
    data_management_plan = models.CharField(max_length=255, choices=type_choices)
    data_contact = models.ManyToManyField(Person)
    last_updated = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return "{}".format(self.project)
