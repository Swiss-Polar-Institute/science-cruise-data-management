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

# Meteorological data
class MetDataAll(models.Model):
    date_time = models.DateTimeField(unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    WD2MA1 = models.FloatField()
    WD2MM1 = models.FloatField()
    WD2MX1 = models.FloatField()
    WS2MA1 = models.FloatField()
    WS2MM1 = models.FloatField()
    WS2MX1 = models.FloatField()
    WD10MA1 = models.FloatField()
    WD10MM1 = models.FloatField()
    WD10MX1 = models.FloatField()
    WS10MA1 = models.FloatField()
    WS10MM = models.FloatField()
    WS10MX1 = models.FloatField()
    WD2MA2 = models.FloatField()
    WD2MM2 = models.FloatField()
    WD2MX2 = models.FloatField()
    WS2MA2 = models.FloatField()
    WS2MM2 = models.FloatField()
    WS2MX2 = models.FloatField()
    WD10MA2 = models.FloatField()
    WD10MX2 = models.FloatField()
    WD10MM2 = models.FloatField()
    WS10MA2 = models.FloatField()
    WS10MX2 = models.FloatField()
    WS10MM2 = models.FloatField()
    VIS = models.FloatField()
    wawa = models.FloatField()
    CL1 = models.FloatField()
    CL2 = models.FloatField()
    CL3 = models.FloatField()
    SC1 = models.FloatField()
    SC2 = models.FloatField()
    SC3 = models.FloatField()
    RH1 = models.FloatField()
    TA1 = models.FloatField()
    DP1 = models.FloatField()
    RH2 = models.FloatField()
    TA2 = models.FloatField()
    DP2 = models.FloatField()
    PA1 = models.FloatField()
    PA2 = models.FloatField()
    SR1 = models.FloatField()
    SR2 = models.FloatField()
    SR3 = models.FloatField()
    UV1 = models.FloatField()
    UV2 = models.FloatField()
    cond = models.FloatField()
    salinity = models.FloatField()
    TwTwTw = models.FloatField()
    TIMEDIFF = models.FloatField()
    CLOUDTEXT = models.FloatField()
    VISCODE = models.FloatField()

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        verbose_name_plural = "Meterological data - full set"

class MetDataWind(models.Model):
    TIME = models.DateTimeField(unique=True, verbose_name="Date time")
    COG = models.FloatField(null=True, blank=True, verbose_name="Course over ground")
    HEADING= models.FloatField(null=True, blank=True, verbose_name="Heading")
    WDR1 = models.FloatField(null=True, blank=True, verbose_name="Relative wind direction 1")
    WSR1 = models.FloatField(null=True, blank=True, verbose_name="Relative wind speed 1")
    WD1 = models.FloatField(null=True, blank=True, verbose_name="Wind direction 1")
    WS1 = models.FloatField(null=True, blank=True, verbose_name="Wind speed 1")
    WDR2 = models.FloatField(null=True, blank=True, verbose_name="Relative wind direction 2")
    WSR2 = models.FloatField(null=True, blank=True, verbose_name="Relative wind speed 2")
    WD2 = models.FloatField(null=True, blank=True, verbose_name="Wind direction 2")
    WS2 = models.FloatField(null=True, blank=True, verbose_name="Wind speed 2")
    TIMEDIFF = models.FloatField(null=True, blank=True, verbose_name="Time difference")
    Year = models.IntegerField(null=True, blank=True)
    Month = models.IntegerField(null=True, blank=True)
    DAY = models.IntegerField(null=True, blank=True)
    CLOUDTEXT = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.TIME)

    class Meta:
        verbose_name_plural = "Meterological data - wind"

