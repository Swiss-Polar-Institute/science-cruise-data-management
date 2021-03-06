from django.db import models
from main.models import SamplingMethod, MeasurelandQualifierFlags
import main.models

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

class Ferrybox(models.Model):
    date_time = models.DateTimeField(db_index=True)
    salinity = models.FloatField()
    oxygen = models.FloatField()
    conductivity = models.FloatField()
    temperature = models.FloatField()
    fluorimeter = models.FloatField()

    class Meta:
        get_latest_by = "date_time"

# GPS data from log files
class GpzdaDateTime(models.Model):
    device = models.ForeignKey(SamplingMethod, on_delete=models.CASCADE)
    date_time = models.DateTimeField(db_index=True)
    local_zone_hours = models.IntegerField()
    local_zone_minutes = models.IntegerField()

    def __str__(self):
        return "main/{}".format(self.date_time)


class GpggaGpsFix(models.Model):
    device = models.ForeignKey(SamplingMethod, on_delete=models.CASCADE)
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
    measureland_qualifier_flags = models.ForeignKey(MeasurelandQualifierFlags, null=True, blank=True,
                                                   default=MeasurelandQualifierFlags.DEFAULT_PK,
                                                    on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        get_latest_by = "date_time"

class GpvtgVelocity(models.Model):
    device = models.ForeignKey(SamplingMethod, on_delete=models.CASCADE)
    date_time = models.DateTimeField(db_index=True)      # not in the gpvtg string, importer will use the time from the prior string
    true_track_deg = models.FloatField()
    magnetic_track_deg = models.FloatField(null=True, blank=True)
    ground_speed_kts = models.FloatField()

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        verbose_name_plural = "Gpvtg Velocities"
        get_latest_by = "date_time"


# Quality-checked cruise track data
class CruiseTrack(models.Model):
    date_time = models.DateTimeField(unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    fix_quality = models.IntegerField(null=True, blank=True)
    number_satellites = models.IntegerField(null=True, blank=True)
    horiz_dilution_of_position = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    altitude_units = models.CharField(max_length=1, null=True, blank=True)
    geoid_height = models.FloatField(null=True, blank=True)
    geoid_height_units = models.CharField(max_length=1, null=True, blank=True)
    device = models.ForeignKey(SamplingMethod, on_delete=models.CASCADE)
    speed = models.FloatField(null=True, blank=True)
    measureland_qualifier_flag_overall = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        verbose_name_plural = "Quality-checked cruise track"


# Meteorological data
class MetDataAll(models.Model):
    date_time = models.DateTimeField(unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    WD2MA1 = models.FloatField(null=True, blank=True)
    WD2MM1 = models.FloatField(null=True, blank=True)
    WD2MX1 = models.FloatField(null=True, blank=True)
    WS2MA1 = models.FloatField(null=True, blank=True)
    WS2MM1 = models.FloatField(null=True, blank=True)
    WS2MX1 = models.FloatField(null=True, blank=True)
    WD10MA1 = models.FloatField(null=True, blank=True)
    WD10MM1 = models.FloatField(null=True, blank=True)
    WD10MX1 = models.FloatField(null=True, blank=True)
    WS10MA1 = models.FloatField(null=True, blank=True)
    WS10MM = models.FloatField(null=True, blank=True)
    WS10MX1 = models.FloatField(null=True, blank=True)
    WD2MA2 = models.FloatField(null=True, blank=True)
    WD2MM2 = models.FloatField(null=True, blank=True)
    WD2MX2 = models.FloatField(null=True, blank=True)
    WS2MA2 = models.FloatField(null=True, blank=True)
    WS2MM2 = models.FloatField(null=True, blank=True)
    WS2MX2 = models.FloatField(null=True, blank=True)
    WD10MA2 = models.FloatField(null=True, blank=True)
    WD10MX2 = models.FloatField(null=True, blank=True)
    WD10MM2 = models.FloatField(null=True, blank=True)
    WS10MA2 = models.FloatField(null=True, blank=True)
    WS10MX2 = models.FloatField(null=True, blank=True)
    WS10MM2 = models.FloatField(null=True, blank=True)
    VIS = models.FloatField(null=True, blank=True)
    wawa = models.FloatField(null=True, blank=True)
    CL1 = models.FloatField(null=True, blank=True)
    CL2 = models.FloatField(null=True, blank=True)
    CL3 = models.FloatField(null=True, blank=True)
    SC1 = models.FloatField(null=True, blank=True)
    SC2 = models.FloatField(null=True, blank=True)
    SC3 = models.FloatField(null=True, blank=True)
    RH1 = models.FloatField(null=True, blank=True)
    TA1 = models.FloatField(null=True, blank=True)
    DP1 = models.FloatField(null=True, blank=True)
    RH2 = models.FloatField(null=True, blank=True)
    TA2 = models.FloatField(null=True, blank=True)
    DP2 = models.FloatField(null=True, blank=True)
    PA1 = models.FloatField(null=True, blank=True)
    PA2 = models.FloatField(null=True, blank=True)
    SR1 = models.FloatField(null=True, blank=True)
    SR2 = models.FloatField(null=True, blank=True)
    SR3 = models.FloatField(null=True, blank=True)
    UV1 = models.FloatField(null=True, blank=True)
    UV2 = models.FloatField(null=True, blank=True)
    cond = models.FloatField(null=True, blank=True)
    salinity = models.FloatField(null=True, blank=True)
    TwTwTw = models.FloatField(null=True, blank=True)
    TIMEDIFF = models.FloatField(null=True, blank=True)
    CLOUDTEXT = models.FloatField(null=True, blank=True)
    VISCODE = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.date_time)

    class Meta:
        verbose_name_plural = "Meterological data - full set"
        get_latest_by = "date_time"


class MetDataWind(models.Model):
    date_time = models.DateTimeField(unique=True, verbose_name="Date time")
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
    CLOUDTEXT = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.TIME)

    class Meta:
        verbose_name_plural = "Meteorological data - wind"
        get_latest_by = "date_time"


class MetDataFile(models.Model):
    file_name = models.CharField(max_length=255)
    date_imported = models.DateTimeField(max_length=255)

    def __str__(self):
        return "{}".format(self.file_name)


class MultibeamRawFileMetadata(models.Model):
    file_path = models.CharField(max_length=300)
    directory = models.CharField(max_length=30)
    swath_data_file = models.CharField(max_length=40)
    file_start_time = models.DateTimeField()
    file_end_time = models.DateTimeField()
    minimum_longitude = models.FloatField()
    maximum_longitude = models.FloatField()
    minimum_latitude = models.FloatField()
    maximum_latitude = models.FloatField()
    minimum_sonar_depth = models.FloatField()
    maximum_sonar_depth = models.FloatField()

    def __str__(self):
        return "{}".format(self.swath_data_file)
