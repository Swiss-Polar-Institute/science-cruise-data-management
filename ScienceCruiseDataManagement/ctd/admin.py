from django.contrib import admin
from ctd.models import CtdBottleTrigger, CtdSampleVolume, CtdVariable

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