from django.contrib import admin
from ctd.models import CtdBottleTrigger, CtdSampleVariable, CtdVariable

class CtdBottleTriggerAdmin(admin.ModelAdmin):
    list_display = ('ctd_cast', 'depth', 'niskin')
    ordering = ['-ctd_cast']

class CtdVariableAdmin(admin.ModelAdmin):
    list_display = ('name', )
    ordering = ['-name']

class CtdSampleVariableAdmin(admin.ModelAdmin):
    list_display = ('ctd_variable', 'volume', 'ctd_bottle_trigger')
    ordering = ['ctd_variable']

admin.site.register(CtdBottleTrigger, CtdBottleTriggerAdmin)
admin.site.register(CtdSampleVariable, CtdSampleVariableAdmin)
admin.site.register(CtdVariable, CtdVariableAdmin)