from django.contrib import admin

import main.models

from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.
# admin.site.register(Project)
admin.site.register(main.models.Country)
admin.site.register(main.models.Instrument)
admin.site.register(main.models.Storage)
admin.site.register(main.models.General_Storage)
admin.site.register(main.models.PositionType)
# admin.site.register(main.models.EventAction)
admin.site.register(main.models.Leg)
admin.site.register(main.models.Port)
admin.site.register(main.models.EventActionType)
admin.site.register(main.models.PositionUncertainty)
admin.site.register(main.models.PositionSource)
admin.site.register(main.models.TimeUncertainty)
admin.site.register(main.models.TimeSource)
admin.site.register(main.models.EventActionDescription)


class ProjectsStartsWithLetter(admin.SimpleListFilter):
    title = "Projects starts with A"
    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        return (('a', 'Starts with A'),
                ('b', 'Starts with B'))

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(name__startswith=self.value())
        else:
            return queryset

class ProjectAdmin(admin.ModelAdmin):
    # list_filter = ('name')
    list_display = ('name', 'country')
    list_filter = (ProjectsStartsWithLetter,)

class EventAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "leg":
            kwargs["queryset"] = main.models.Leg.objects.filter(name="Leg 1")
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class PositionResource(resources.ModelResource):
    class Meta:
        model = main.models.Position


class PositionAdmin(ImportExportModelAdmin):
    list_display=('number', 'text', 'latitude', 'longitude')
    ordering = ('number',)
    resource_class = PositionResource
    search_fields = ['text']
    # exclude = ('text',)

class EventActionAdmin(ImportExportModelAdmin):
    list_display = ('event_id', 'date_time', 'latitude', 'longitude')
    ordering = ['event_id']


admin.site.register(main.models.Project, ProjectAdmin)
admin.site.register(main.models.Position, PositionAdmin)
admin.site.register(main.models.EventAction, EventActionAdmin)
admin.site.register(main.models.Event, EventAdmin)