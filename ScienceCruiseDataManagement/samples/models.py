from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django_mysql.models import JSONField
from django.conf import settings

import django.apps

from main.models import default_mission_id, current_active_leg_id
from django.db.models.signals import post_save

# User = django.apps.apps.get_model("main", "User")


class StorageType(models.Model):
    from main.models import User
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_on_date_time = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.name)


class Preservation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.name)


class Sample(models.Model):
    from main.models import Ship
    # It's updated by the function update_expedition_sample_code. But it's null for a moment while we get the
    # ID since the expedition_sample_code has the primary key of this table. So it needs to be stored
    # and then updated.
    expedition_sample_code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    project_sample_number = models.CharField(max_length=255, null=True, blank=True)
    contents = models.CharField(max_length=255)
    crate_number = models.CharField(max_length=255, null=True, blank=True)
    storage_type = models.ForeignKey(StorageType, null=True, blank=True, on_delete=models.CASCADE)
    storage_location = models.CharField(max_length=255, null=True, blank=True)
    offloading_port = models.CharField(max_length=255)
    destination = models.CharField(max_length=255, null=True, blank=True)
    ship = models.ForeignKey(Ship, null=True, blank=True, on_delete=models.CASCADE)
    mission = models.ForeignKey('main.Mission', default=default_mission_id, on_delete=models.CASCADE)
    leg = models.ForeignKey('main.Leg', default=current_active_leg_id, on_delete=models.CASCADE)
    project = models.ForeignKey('main.Project', on_delete=models.CASCADE)
    julian_day = models.IntegerField()
    event = models.ForeignKey('main.Event', on_delete=models.CASCADE)
    pi = models.ForeignKey('main.Person', on_delete=models.CASCADE)
    preservation = models.ForeignKey(Preservation, blank=True, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    file = models.CharField(max_length=255, blank=True, null=True)
    specific_contents = models.CharField(max_length=255, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
    other_data = JSONField()

    def __str__(self):
        return "{}".format(self.expedition_sample_code)


@receiver(post_save, sender=Sample)
def update_expedition_sample_code(sender, instance, **kwargs):
    # It's done in the post_save because the sample_id can be part of the expedition_sample_code
    if instance.expedition_sample_code is None or instance.expedition_sample_code == '':
        instance.expedition_sample_code = settings.EXPEDITION_SAMPLE_CODE(instance)
        instance.save()
