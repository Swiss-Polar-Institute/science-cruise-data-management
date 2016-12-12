from django.contrib import admin

import main.models
import import_export
from django.db.models import Q

# Register your models here.
admin.site.register(main.models.Country)
admin.site.register(main.models.Storage)
admin.site.register(main.models.General_Storage)
admin.site.register(main.models.PositionType)
admin.site.register(main.models.Port)
admin.site.register(main.models.PositionUncertainty)
admin.site.register(main.models.PositionSource)
admin.site.register(main.models.TimeUncertainty)
admin.site.register(main.models.TimeSource)
admin.site.register(main.models.Preservation)
admin.site.register(main.models.SpeciesClassification)
admin.site.register(main.models.SampleContent)
admin.site.register(main.models.Sample)
admin.site.register(main.models.Person)
admin.site.register(main.models.Organisation)
admin.site.register(main.models.Data)


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
    list_display = ('number', 'title', 'alternative_title', 'principal_investigator', 'abstract')
    list_filter = (ProjectsStartsWithLetter,)


class EventResource(import_export.resources.ModelResource):
    number = import_export.fields.Field(column_name = 'number', attribute='number')

    station = import_export.fields.Field(
        column_name = 'station',
        attribute = 'station',
        widget = import_export.widgets.ForeignKeyWidget(main.models.Station, 'name')
    )

    class Meta:
        fields = ('number', 'station', 'device', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude')


class EventAdmin(import_export.admin.ImportExportModelAdmin):
    list_display = ('number', 'station', 'device', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude')
    ordering = ['-number']
    resource_class = EventResource

    def start_time(self, obj):
        event_id = obj.id
        begins = main.models.EventActionType.objects.filter(code="TBEGINS")
        print(begins())
        start_time = main.models.EventAction.objects.filter(Q(id=event_id) | Q(type=begins))

        if len(start_time) > 0:
            return start_time.time

        return obj.station.arrival_time

    def start_latitude(self, obj):
        return obj.station.latitude

    def start_longitude(self, obj):
        return obj.station.longitude

    def end_time(self, obj):
        return obj.station.departure_time

    def end_latitude(self, obj):
        return obj.station.latitude

    def end_longitude(self, obj):
        return 'TODO'

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
        fields = ('date_time', 'latitude', 'longitude','date_time', 'type_description__name')


class EventActionAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    #def description_2(self, obj):
    #    return obj.event_action_type.description

    #description_2.short_description = "Description"

    list_display = ('time', 'latitude', 'longitude', 'position_uncertainty') #, 'description_2')
    ordering = ['event_id']

    resource_class = EventActionResource


class EventActionDescriptionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    ordering = ['code']


class LegAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'start_port', 'start_time', 'end_port', 'end_time')
    ordering = ['number']


class StationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'leg_number', 'latitude', 'longitude', 'arrival_time', 'departure_time', 'list_deployed_devices')
    ordering = ['name']

    def leg_number(self, obj):
        return obj.leg.number

    def list_deployed_devices(self, obj):
        return "TODO"


class EventReportAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'station_name', 'device_name', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude')

    def station_name(self, obj):
        return obj.station.name

    def device_name(self, obj):
        return obj.device.name

    def _get_event_action(self, start_or_end, event_id, field):
        """ Returns the Event Action start (where type="TBEGNS" or "TINSTANT" and the EventId is
            the same as event_id
        """
        if start_or_end == "start":
            start_or_end = "TBEGNS"
        elif start_or_end == "end":
            start_or_end = "TENDS"
        else:
            assert False

        result = main.models.EventAction.objects.all().filter((Q(type=start_or_end) | Q(type="TINSTNAT")) & Q(event_id=event_id))
        if len(result) > 0:
            return getattr(result[0], field)
        else:
            return None

    def _get_event_action_start(self, event_id, field):
        return self._get_event_action('start', event_id, field)

    def _get_event_action_end(self, event_id, field):
        return self._get_event_action('end', event_id, field)

    def start_time(self, obj):
        return self._get_event_action_start(obj.id, 'time')

    def start_latitude(self, obj):
        return self._get_event_action_start(obj.id, 'latitude')

    def start_longitude(self, obj):
        return self._get_event_action_start(obj.id, 'longitude')

    def end_time(self, obj):
        return self._get_event_action_end(obj.id, 'time')

    def end_latitude(self, obj):
        return self._get_event_action_end(obj.id, 'latitude')

    def end_longitude(self, obj):
        return self._get_event_action_end(obj.id, 'longitude')


class StationTypeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('type', )


class DeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name')



admin.site.register(main.models.Device, DeviceAdmin)
admin.site.register(main.models.StationType, StationTypeAdmin)
admin.site.register(main.models.Project, ProjectAdmin)
admin.site.register(main.models.Position, PositionAdmin)
admin.site.register(main.models.Event, EventAdmin)
admin.site.register(main.models.EventActionDescription, EventActionDescriptionAdmin)
admin.site.register(main.models.EventAction, EventActionAdmin)
admin.site.register(main.models.Station, StationAdmin)
admin.site.register(main.models.Leg, LegAdmin)
admin.site.register(main.models.EventReport, EventReportAdmin)

admin.site.site_header = 'ACE Data'
admin.site.site_title = 'ACE Data Admin'
admin.site.site_header = 'ACE Data Administration'