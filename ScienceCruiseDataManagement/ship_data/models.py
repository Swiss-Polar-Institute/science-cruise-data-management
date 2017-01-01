from django.db import models
from main.models import ParentDevice


# GPS data from log files
class GpzdaDateTime(models.Model):
    device = models.ForeignKey(ParentDevice)
    date_time = models.DateTimeField(db_index=True)
    local_zone_hours = models.IntegerField()
    local_zone_minutes = models.IntegerField()

    def __str__(self):
        return "main/{}".format(self.date_time)

class GpggaGpsFix(models.Model):
    device = models.ForeignKey(ParentDevice)
    date_time = models.DateTimeField(db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    fix_quality = models.PositiveSmallIntegerField()
    number_satellites = models.PositiveSmallIntegerField()
    horiz_dilution_of_position = models.FloatField()
    altitude= models.FloatField()
    altitude_units = models.CharField(max_length=1)
    geoid_height = models.FloatField(null=True, blank=True)
    geoid_height_units = models.CharField(null=True, blank=True, max_length=1)

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        get_latest_by = "date_time"

class GpvtgVelocity(models.Model):
    device = models.ForeignKey(ParentDevice)
    date_time = models.DateTimeField(db_index=True)      # not in the gpvtg string, importer will use the time from the prior string
    true_track_deg = models.FloatField()
    magnetic_track_deg = models.FloatField(null=True, blank=True)
    ground_speed_kts = models.FloatField()

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        verbose_name_plural = "Gpvtg Velocities"
