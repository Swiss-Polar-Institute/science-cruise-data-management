from django.contrib import admin
from django.db import models
import ship_data.models
import import_export


class GpzdaDateTimeAdminAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'local_zone_hours', 'local_zone_minutes', 'device')
    ordering = ['-date_time']


class GpvtgVelocityAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'true_track_deg', 'magnetic_track_deg', 'ground_speed_kts', 'device')
    ordering = ['-date_time']


class GpggaGpsFixAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'latitude', 'longitude', 'fix_quality', 'number_satellites', 'horiz_dilution_of_position', 'altitude', 'altitude_units', 'geoid_height', 'geoid_height_units', 'device')
    ordering = ['-date_time']

class MetDataAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'latitude', 'longitude', 'WD2MA1', 'WD2MM1', 'WD2MX1', 'WS2MA1', 'WS2MM1', 'WS2MX1', 'WD10MA1', 'WD10MM1', 'WD10MX1', 'WS10MA1', 'WS10MM', 'WS10MX1', 'WD2MA2', 'WD2MM2', 'WD2MX2', 'WS2MA2', 'WS2MM2', 'WS2MX2', 'WD10MA2', 'WD10MX2', 'WD10MM2', 'WS10MA2', 'WS10MX2', 'WS10MM2', 'VIS', 'wawa', 'CL1', 'CL2', 'CL3', 'SC1', 'SC2', 'SC3', 'RH1', 'TA1', 'DP1', 'RH2', 'TA2', 'DP2', 'PA1', 'PA2', 'SR1', 'SR2', 'SR3', 'UV1', 'UV2', 'cond', 'salinity', 'TwTwTw', 'TIMEDIFF', 'CLOUDTEXT', 'VISCODE')
    ordering = ['date_time']


    # Register your models here.
admin.site.register(ship_data.models.GpzdaDateTime, GpzdaDateTimeAdminAdmin)
admin.site.register(ship_data.models.GpvtgVelocity, GpvtgVelocityAdmin)
admin.site.register(ship_data.models.GpggaGpsFix, GpggaGpsFixAdmin)
admin.site.register(ship_data.models.MetData, MetDataAdmin)