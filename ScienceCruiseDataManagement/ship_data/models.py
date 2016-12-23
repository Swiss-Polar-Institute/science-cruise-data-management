from django.db import models

# Create your models here.

# GPS data from log files
class GpzdaDateTime(models.Model):
    date_time = models.DateTimeField(unique=True)
    local_zone_hours = models.IntegerField()
    local_zone_minutes = models.IntegerField()

    def __str__(self):
        return "{}".format(self.time)

class GpggaGpsFix(models.Model):
    date_time = models.DateTimeField(unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    fix_quality = models.PositiveSmallIntegerField()
    number_satellites = models.PositiveSmallIntegerField()
    horiz_dilution_of_position = models.FloatField()
    altitude= models.FloatField()
    altitude_units = models.CharField(max_length=1)
    geoid_height = models.FloatField()
    geoid_height_units = models.CharField(max_length=1)

    def __str__(self):
        return "{}".format(self.time)

class GpvtgVelocity(models.Model):
    date_time = models.DateTimeField(unique=True)      # not in the gpvtg string, importer will use the time from the prior string
    true_track_deg = models.FloatField()
    magnetic_track_deg = models.FloatField()
    ground_speed_kts = models.FloatField()

    def __str__(self):
        return "{}".format(self.time)
