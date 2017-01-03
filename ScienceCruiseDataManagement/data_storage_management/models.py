from django.db import models
from main.models import Person, DeviceType
import django.utils.timezone
from django.core.exceptions import ValidationError


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
    source_directory = models.CharField(max_length=255, help_text="If it's a directory make sure that ends with / to avoid creating subdirectories. If it's a file(s) then make sure to not have it so it copies them")
    destination_directory = models.CharField(max_length=255, unique=True, help_text="Can't start with /, it's a relative path")

    # A directory should come from only one of these sources
    hard_disk = models.ForeignKey(HardDisk, null=True, blank=True)
    shared_resource = models.ForeignKey(SharedResource, null=True, blank=True)
    nas_resource = models.ForeignKey(NASResource, null=True, blank=True)

    added_date_time  = models.DateTimeField(default=django.utils.timezone.now)

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
        if self.hard_disk is None and self.shared_resource is None and self.nas_resource is None:
            raise ValidationError("Please select where to copy this directory/file form: hard disk, shared resource or NAS")

        directories_errors = {}
        if self.destination_directory.startswith("/"):
            directories_errors['destination_directory'] = "Destination directory cannot start with /"
        if not self.source_directory.startswith("/"):
            directories_errors['source_directory'] = "Source directory has to start with /"

        if len(directories_errors) > 0:
            raise ValidationError(directories_errors)


class Directory(Item):
    class Meta:
        verbose_name_plural = "Directories"


class File(Item):
    pass


class DirectoryImportLog(models.Model):
    directory = models.ForeignKey(Directory)
    updated_time = models.DateTimeField(default=django.utils.timezone.now)
    success = models.BooleanField()
