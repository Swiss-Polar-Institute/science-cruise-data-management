from django.db import models
from main.models import CtdCast
from main.models import Person

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

class CtdBottleTrigger(models.Model):
    ctd_cast = models.ForeignKey(CtdCast, on_delete=models.CASCADE)
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
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    principal_investigator = models.ForeignKey(Person, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'principal_investigator'),)

    def __str__(self):
        return "{}".format(self.name)


class CtdSampleVolume(models.Model):
    ctd_variable = models.ForeignKey(CtdVariable, on_delete=models.CASCADE)
    volume = models.FloatField(blank=True, null=True, help_text="Blank if unknown")
    ctd_bottle_trigger = models.ForeignKey(CtdBottleTrigger, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('ctd_variable', 'ctd_bottle_trigger'),)

    def __str__(self):
        return "{} {} {}".format(self.ctd_variable, self.volume, self.ctd_bottle_trigger)
