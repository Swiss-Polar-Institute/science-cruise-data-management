from django.contrib import admin
from ctd.models import CtdBottleTrigger, CtdSampleVolume, CtdVariable


class CtdBottleTriggerInLine(admin.TabularInline):
    model = CtdBottleTrigger
    extra = 0


class CtdSampleVolumeInLine(admin.TabularInline):
    model = CtdSampleVolume
    extra = 0

class CtdBottleTriggerAdmin(admin.ModelAdmin):
    list_display = ('ctd_cast_info', 'depth', 'niskin')
    ordering = ['-ctd_cast']

    def ctd_cast_info(self, obj):
        return "Event: {} Cast: {} Leg: {}".format(obj.ctd_cast.event_number.number, obj.ctd_cast, obj.ctd_cast.leg_number)

    inlines = [CtdSampleVolumeInLine]

class CtdVariableAdmin(admin.ModelAdmin):
    list_display = ('name', )
    ordering = ['-name']

class CtdSampleVolumeAdmin(admin.ModelAdmin):
    list_display = ('ctd_variable', 'volume', 'ctd_bottle_trigger')
    ordering = ['ctd_variable']

admin.site.register(CtdBottleTrigger, CtdBottleTriggerAdmin)
admin.site.register(CtdSampleVolume, CtdSampleVolumeAdmin)
admin.site.register(CtdVariable, CtdVariableAdmin)