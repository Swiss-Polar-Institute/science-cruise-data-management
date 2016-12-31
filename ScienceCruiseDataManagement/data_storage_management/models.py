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
    source_directory = models.CharField(max_length=255)
    destination_directory = models.CharField(max_length=255, unique=True)

    # A directory should come from only one of these sources
    hard_disk = models.ForeignKey(HardDisk, null=True, blank=True)
    shared_resource = models.ForeignKey(SharedResource, null=True, blank=True)
    nas_resource = models.ForeignKey(NASResource, null=True, blank=True)

    # TODO: validate that the destination path doesn't end in "/"
    created_date_time = models.DateTimeField(default=django.utils.timezone.now)

    added_date_time = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return "{}-{}".format(self.source_directory, self.destination_directory)


class Directory(Item):
    class Meta:
        verbose_name_plural = "Directories"


class File(Item):
    pass


class DirectoryImportLog(models.Model):
    directory = models.ForeignKey(Directory)
    updated_time = models.DateTimeField(default=django.utils.timezone.now)
    success = models.BooleanField()

    class Meta:
        verbose_name_plural="Directory Updates"
