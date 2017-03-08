from django.db import models
from main.models import CtdCast


class CtdBottleTrigger(models.Model):
    ctd_cast = models.ForeignKey(CtdCast)
    depth = models.IntegerField()
    niskin = models.IntegerField()

    def __str__(self):
        return "Event number: {} Depth: {} Nisking bottle: {}".format(self.ctd_cast.event_number,
                                                                      self.depth,
                                                                      self.niskin)


class CtdVariable(models.Model):
    name = models.CharField(max_length=255, unique=True)


class CtdSampleVariable(models.Model):
    ctd_variable = models.ForeignKey(CtdVariable)
    volume = models.FloatField(blank=True, null=True)
    ctd_bottle_trigger = models.ForeignKey(CtdBottleTrigger)

