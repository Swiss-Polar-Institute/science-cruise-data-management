from django.db import models
from main.models import Person
import django.utils.timezone


class HardDisk(models.Model):
    uuid = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    created_date_time = models.DateTimeField(default=django.utils.timezone.now)
    person = models.ForeignKey(Person, null=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.uuid)


class Directory(models.Model):
    source_path = models.CharField(max_length=255)
    destination_path = models.CharField(max_length=255, unique=True)
    hard_disk = models.ForeignKey(HardDisk)
    # TODO: validate that the destination path doesn't end in "/"
    created_date_time = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return "{}-{}".format(self.source_path, self.destination_path)

    class Meta:
        verbose_name_plural="Directories"