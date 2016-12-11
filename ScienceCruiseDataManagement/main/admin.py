from django.contrib import admin

import main.models

import import_export

# Register your models here.
admin.site.register(main.models.Country)
admin.site.register(main.models.Device)
admin.site.register(main.models.Storage)
admin.site.register(main.models.General_Storage)
admin.site.register(main.models.PositionType)
admin.site.register(main.models.Leg)
admin.site.register(main.models.Port)
admin.site.register(main.models.EventActionType)
admin.site.register(main.models.PositionUncertainty)
admin.site.register(main.models.PositionSource)
admin.site.register(main.models.TimeUncertainty)
admin.site.register(main.models.TimeSource)
admin.site.register(main.models.Preservation)
admin.site.register(main.models.SpeciesClassification)
admin.site.register(main.models.SampleContent)
admin.site.register(main.models.Sample)
admin.site.register(main.models.Station)
admin.site.register(main.models.StationType)


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


class EventResource(import_export.resources.ModelResource):
    number = import_export.fields.Field(column_name = 'number', attribute='number')

    station = import_export.fields.Field(
        column_name = 'station',
        attribute = 'station',
        widget = import_export.widgets.ForeignKeyWidget(main.models.Station, 'name')
    )

    class Meta:
        fields = ('number', 'station', 'device', )


class EventAdmin(import_export.admin.ImportExportModelAdmin):
    list_display = ('number', 'station', 'device')
    ordering = ['-number']
    resource_class = EventResource

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "leg":
            kwargs["queryset"] = main.models.Leg.objects.filter(name="Leg 1")
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PositionResource(import_export.resources.ModelResource):
    class Meta:
        model = main.models.Position


class PositionAdmin(import_export.admin.ImportExportModelAdmin):
    list_display=('number', 'text', 'latitude', 'longitude')
    ordering = ('number',)
    resource_class = PositionResource
    search_fields = ['text']
    # exclude = ('text',)


class EventActionResource(import_export.resources.ModelResource):
   class Meta:
        model = main.models.EventAction
        fields = ('date_time', 'latitude', 'longitude','date_time', 'event_action_type__description')


class EventActionAdmin(import_export.admin.ImportExportModelAdmin):
    def description_2(self, obj):
        return obj.event_action_type.description

    description_2.short_description = "Description"

    list_display = ('date_time', 'latitude', 'longitude', 'position_uncertainty', 'description_2')
    ordering = ['event_id']

    resource_class = EventActionResource


class EventActionDescriptionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    ordering = ['code']


admin.site.register(main.models.Project, ProjectAdmin)
admin.site.register(main.models.Position, PositionAdmin)
admin.site.register(main.models.Event, EventAdmin)
admin.site.register(main.models.EventActionDescription, EventActionDescriptionAdmin)
admin.site.register(main.models.EventAction, EventActionAdmin)

admin.site.site_header = 'ACE Data'
admin.site.site_title = 'ACE Data Admin'
admin.site.site_header = 'ACE Data Administration'