from django.db import models
from main.models import Person, DeviceType
import django.utils.timezone


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
    comment = models.TextField(null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "//{}/{}".format(self.ip, self.shared_resource)


class NASDirectory(models.Model):
    shared_resource = models.CharField(max_length=255)
    added_date_time = models.DateTimeField(default=django.utils.timezone.now)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.shared_resource)

    class Meta:
        verbose_name_plural = "NAS Directories"


class Item(models.Model):
    source_path = models.CharField(max_length=255)
    destination_path = models.CharField(max_length=255, unique=True)

    # A directory should come from only one of these sources
    hard_disk = models.ForeignKey(HardDisk, null=True)
    shared_resource = models.ForeignKey(SharedResource, null=True)
    staging_directory = models.ForeignKey(NASDirectory, null=True)

    # TODO: validate that the destination path doesn't end in "/"
    created_date_time = models.DateTimeField(default=django.utils.timezone.now)

    added_date_time = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return "{}-{}".format(self.source_path, self.destination_path)


class Directory(Item):
    class Meta:
        verbose_name_plural = "Directories"


class File(Item):
    pass


class DirectoryUpdates(models.Model):
    directory = models.ForeignKey(Directory)
    updated_time = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        verbose_name_plural="Directory Updates"
