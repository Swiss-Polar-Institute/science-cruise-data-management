from django.db import models

# Create your models here.

# GPS data from log files
class GpzdaDateTime(models.Model):
    time = models.CharField(max_length=9, unique=True)
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    local_zone_hours = models.IntegerField()
    local_zone_minutes = models.IntegerField()

    def __str__(self):
        return "{}".format(self.time)

class GpggaGpsFix(models.Model):
    time = models.CharField(max_length=9, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    fix_quality = models.IntegerField()
    number_satellites = models.IntegerField()
    horiz_dilution_of_position = models.FloatField()
    altitude= models.FloatField()
    altitude_units = models.CharField(max_length=1)
    geoid_height = models.FloatField()
    geoid_height_units = models.CharField(max_length=1)

    def __str__(self):
        return "{}".format(self.time)

class GpvtgVelocity(models.Model):
    time = models.CharField(max_length=9, unique=True)      # not in the gpvtg string, importer will use the time from the prior string
    true_track_deg = models.FloatField()
    magnetic_track_deg = models.FloatField()
    ground_speed_kts = models.FloatField()

    def __str__(self):
        return "{}".format(self.time)
