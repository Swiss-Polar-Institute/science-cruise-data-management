from django.db import models
from main.models import CtdCast


class CtdBottleTrigger(models.Model):
    ctd_cast = models.ForeignKey(CtdCast)
    depth = models.IntegerField()
    niskin = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('ctd_cast', 'depth', 'niskin'),)

    def __str__(self):
        return "Event number: {} Depth: {} Nisking bottle: {} Comment: {}".format(self.ctd_cast.event_number,
                                                                      self.depth,
                                                                      self.niskin,
                                                                      self.comment)


class CtdVariable(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "{}".format(self.name)


class CtdSampleVolume(models.Model):
    ctd_variable = models.ForeignKey(CtdVariable)
    volume = models.FloatField(blank=True, null=True)
    ctd_bottle_trigger = models.ForeignKey(CtdBottleTrigger)

    class Meta:
        unique_together = (('ctd_variable', 'ctd_bottle_trigger'),)

    def __str__(self):
        return "{} {} {}".format(self.ctd_variable, self.volume, self.ctd_bottle_trigger)
