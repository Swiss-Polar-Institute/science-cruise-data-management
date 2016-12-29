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

# Register your models here.
admin.site.register(ship_data.models.GpzdaDateTime, GpzdaDateTimeAdminAdmin)
admin.site.register(ship_data.models.GpvtgVelocity, GpvtgVelocityAdmin)
admin.site.register(ship_data.models.GpggaGpsFix, GpggaGpsFixAdmin)