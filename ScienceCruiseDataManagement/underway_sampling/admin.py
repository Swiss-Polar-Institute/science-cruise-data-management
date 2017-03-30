from django.contrib import admin
import underway_sampling.models


class UnderwaySamplingVariableAdmin(admin.ModelAdmin):
    list_display = ('name', )


class WhenAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'comment', )


class UnderwaySamplingAdmin(admin.ModelAdmin):
    list_display = ('project', 'when_list', 'what_list', )

    def when_list(self, obj):
        whens = obj.when.all()

        return ", ".join([when.frequency for when in whens])


    def what_list(self, obj):
        whats = obj.what.all()

        return ", ".join([what.name for what in whats])

admin.site.register(underway_sampling.models.UnderwaySamplingVariable, UnderwaySamplingVariableAdmin)
admin.site.register(underway_sampling.models.When, WhenAdmin)
admin.site.register(underway_sampling.models.UnderwaySampling, UnderwaySamplingAdmin)
