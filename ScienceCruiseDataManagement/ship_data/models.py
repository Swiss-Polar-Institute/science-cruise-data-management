from django.db import models

# Create your models here.

# GPS data from log files
class GpzdaDateTime(models.Model):
    nmea_string = models.CharField(max_length=255)
    time = models.FloatField()
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    local_zone_hours = models.IntegerField()
    local_zone_minutes = models.IntegerField()
    checksum = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.time)

class GpggsGpsFix(models.Model):
    nmea_string= models.CharField(max_length=255)
    time = models.FloatField()
    latitude = models.FloatField()
    lat_ns = models.CharField(max_length=255)
    longitude = models.FloatField()
    lon_ew = models.CharField(max_length=255)
    fix_quality = models.IntegerField()
    no_satellites= models.IntegerField()
    horiz_dilution_of_position = models.FloatField()
    altitude= models.FloatField()
    altitude_units = models.CharField(max_length=255)
    geoid_height = models.FloatField()
    geoid_height_units = models.CharField(max_length=255)
    checksum = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.time)

class GpvtgVelocity(models.Model):
    nmea_string = models.CharField(max_length=255)
    time = models.FloatField()
    true_track_deg = models.FloatField()
    magnetic_track_deg = models.FloatField()
    ground_speed_kts = models.FloatField()
    ground_speed_kmh = models.FloatField()
    checksum = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.time)


