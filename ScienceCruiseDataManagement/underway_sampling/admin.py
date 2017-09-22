from django.contrib import admin
import underway_sampling.models

# Note that the script that enters data into these database tables may no longer work because additional fields have been added to the tables.  

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

class UnderwaySamplingVariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', )


class WhenAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'comment', )


class UnderwaySamplingAdmin(admin.ModelAdmin):
    list_display = ('project', 'when_list', 'what_list', )
    ordering = ('project', )

    def when_list(self, obj):
        whens = obj.when.all()

        return ", ".join([when.frequency for when in whens])

    def what_list(self, obj):
        whats = obj.what.all()

        return ", ".join([what.name for what in whats])

admin.site.register(underway_sampling.models.UnderwaySamplingVariable, UnderwaySamplingVariableAdmin)
admin.site.register(underway_sampling.models.When, WhenAdmin)
admin.site.register(underway_sampling.models.UnderwaySampling, UnderwaySamplingAdmin)
