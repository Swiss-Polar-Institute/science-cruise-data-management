from django.contrib import admin
from django.forms import ModelForm
import main.models
import import_export
from django.db.models import Q
import main.utils
from selectable.forms import AutoCompleteSelectField, AutoCompleteSelectMultipleWidget, AutoComboboxSelectWidget
import main.lookups
from django.conf import settings


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
    list_display = ('number', 'title', 'alternative_title', 'principal_investigator', 'abstract')
    list_filter = (ProjectsStartsWithLetter,)
    ordering = ['number']


class ReadOnlyFields:
    def get_readonly_fields(self, request, obj=None):
        if not main.utils.can_user_change_events(request.path, request.user):
            fields_from_model = []

            # Here we want the fields of the model but without the 'related_field'.
            # E.g. if another model had a foreign key to this object with a 'related_name'
            # this appeared here but because it's not in this form the template
            # raised an exception (as it was included)
            for field in self.model._meta.get_fields(include_parents=False):
                if hasattr(self.model, field.name) and not hasattr(field, 'related_name'):
                    fields_from_model.append(field.name)

            return fields_from_model

        return []

        # Example for import-export
#class EventResource(import_export.resources.ModelResource):
#    number = import_export.fields.Field(column_name = 'number', attribute='number')
#
#    station = import_export.fields.Field(
#        column_name = 'station',
#        attribute = 'station',
#        widget = import_export.widgets.ForeignKeyWidget(main.models.Station, 'name')
#    )

    class Meta:
        fields = ('number', 'station', 'device', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude')


class ChildDeviceForm(ModelForm):
    # The AutoCompleteSelectField is disabled because this widget didn't work correctly
    # type_of_device = AutoCompleteSelectField(lookup_class=main.lookups.DeviceTypeLookup, allow_new=False)

    class Meta:
        model = main.models.ChildDevice
        fields = '__all__'


class EventForm(ModelForm):
    class Meta:
        model = main.models.Event
        exclude = ('child_devices', )
        # 'child_device' is not here on purpose, for now

class EventAdmin(ReadOnlyFields, import_export.admin.ImportExportModelAdmin):
    list_display = ('number', 'parent_device', 'station', 'data', 'samples', 'fail')
    ordering = ['-number']

    # add for import-export: resource_class = EventResource

    # This is to have a default value on the foreign key
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "leg":
            kwargs["queryset"] = main.models.Leg.objects.filter(name="Leg 1")
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def get_fields(self, request, obj=None):
        fields = list(self.list_display)

        # never shown, it's the Primary Key
        fields.remove('number')

        if request.user.is_superuser:
            return tuple(fields)
        else:
            # non super users can't mark an event as failed
            fields.remove('fail')
            return tuple(fields)

    form = EventForm

#
#class PositionResource(import_export.resources.ModelResource):
#    class Meta:
#        model = main.models.Position


#class PositionAdmin(import_export.admin.ImportExportModelAdmin):
#    list_display=('number', 'text', 'latitude', 'longitude')
#    ordering = ('number',)
#    resource_class = PositionResource
#    search_fields = ['text']
    # exclude = ('text',)


#class EventActionResource(import_export.resources.ModelResource):
#    class Meta:
#        model = main.models.EventAction
#        fields = ('date_time', 'latitude', 'longitude','date_time', 'type_description__name')

class EventActionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventActionForm, self).__init__(*args, **kwargs)
        # filter out closed events

        if 'event' in self.fields and self._adding_new_event_action():
            # event is not in the fields if it's readonly
            # if we are adding a new event action we don't filter it
            filter_by = self._filter_open_events()
            self.fields['event'].queryset = main.models.Event.objects.all().filter(filter_by)

    def _adding_new_event_action(self):
        # Returns True if the user is adding an event (instead of modifying it)
        # The reason is that we want to show all the events (and not only the open ones) if
        # the user is trying to modify an eventAction. When adding we only show the
        # ones that the user should select.
        return len(self.fields) == 0

    def _filter_open_events(self):
        filter_query = Q(number=0) # Impossible with OR will be the rest

        for open_event_id in self._open_event_numbers():
                filter_query = filter_query | Q(number=open_event_id)

        return filter_query

    def _action_finished(self, event_action_id, event_number):
        event_actions_instant = main.models.EventAction.objects.all().filter(
                                Q(id=event_action_id) & Q(type="TINSTANT"))

        if len(event_actions_instant) > 0:
            print("tinstant: event_action_id:", event_action_id, "event_number:", event_number)
            return True

        event_actions = main.models.EventAction.objects.all().filter(Q(event=event_number) & Q(type="TENDS"))

        if len(event_actions) > 0:
            print("tends: event_action_id:", event_action_id, "event_number:", event_number)
            # There is an TENDS event so it's finished
            return True

        return False

    def _event_not_opened(self, event_id):
        print(event_id)
        other_events = main.models.EventAction.objects.all().filter(Q(event_id=event_id))

        if len(other_events) == 0:
            return True
        else:
            return False

    def _open_event_numbers(self):
        """ Returns the event IDs that have been started and not finished. """
        started_not_finished = []
        event_actions = main.models.EventAction.objects.all()
        events = main.models.Event.objects.all()
        open_event_numbers = []

        # Adds events with TBEGNS and not finished
        for event_action in event_actions:
            if event_action.type == main.models.EventAction.tbegin():
                if not self._action_finished(event_action.id, event_action.event.number):
                    open_event_numbers.append(event_action.event.number)

        for event in events:
            if self._event_not_opened(event.number):
                open_event_numbers.append(event.number)

        return open_event_numbers

    class Meta:
        model = main.models.EventAction
        fields = '__all__'


class EventActionAdmin(ReadOnlyFields, import_export.admin.ExportMixin, admin.ModelAdmin):
    #def description_2(self, obj):
    #    return obj.event_action_type.description

    #description_2.short_description = "Description"

    list_display = ('id', 'event', 'sampling_method', 'type', 'description', 'time', 'time_source', 'time_uncertainty', 'latitude', 'longitude', 'position_source', 'position_uncertainty', 'water_depth', 'general_comments', 'data_source_comments')
    ordering = ['-event_id', '-id']
    form = EventActionForm

    def sampling_method(self, object):
        return object.event.parent_device

    sampling_method.admin_order_field = "event__parent_device"

class EventActionDescriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'source')
    ordering = ['name']


class LegAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'start_time', 'start_port', 'end_time', 'end_port', 'active_leg')
    ordering = ['number']

    def active_leg(self, obj):
        return obj == main.models.Leg.current_active_leg()


class StationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'type', 'latitude', 'longitude', 'leg', 'arrival_time', 'departure_time', 'time_source', 'time_uncertainty', 'position_source', 'position_uncertainty', 'water_depth', 'comment')
    ordering = ['name']


class EventReportAdmin(ReadOnlyFields, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'station_name', 'device_name', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude')

    def station_name(self, obj):
        if obj.station is None:
            return "-"
        else:
            return obj.station.name

    def device_name(self, obj):
        return obj.parent_device.name

    def _get_event_action(self, start_or_end, event_id, field):
        """ Returns the Event Action start (where type="TBEGNS" or "TINSTANT" and the EventId is
            the same as event_id
        """
        if start_or_end == "start":
            start_or_end = main.models.EventAction.tbegin()
        elif start_or_end == "end":
            start_or_end = main.models.EventAction.tends()
        else:
            assert False

        result = main.models.EventAction.objects.all().filter((Q(type=start_or_end) | Q(type="TINSTANT")) & Q(event_id=event_id))
        if len(result) > 0:
            return getattr(result[0], field)
        else:
            return None

    def _get_event_action_start(self, event_id, field):
        return self._get_event_action('start', event_id, field)

    def _get_event_action_end(self, event_id, field):
        return self._get_event_action('end', event_id, field)

    def start_time(self, obj):
        return self._get_event_action_start(obj.number, 'time')

    def start_latitude(self, obj):
        return self._get_event_action_start(obj.number, 'latitude')

    def start_longitude(self, obj):
        return self._get_event_action_start(obj.number, 'longitude')

    def end_time(self, obj):
        return self._get_event_action_end(obj.number, 'time')

    def end_latitude(self, obj):
        return self._get_event_action_end(obj.number, 'latitude')

    def end_longitude(self, obj):
        return self._get_event_action_end(obj.number, 'longitude')


class StationTypeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('type', 'description')
    ordering = ['type']


class ChildDeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('device_type_name', 'serial_number')

    def device_type_name(self, obj):
        return obj.type_of_device.name

    # TODO: doesn't work here, check it again
    # ordering = ['device_type_name__name']

    device_type_name.admin_order_field = 'device_type_name__name'
    form = ChildDeviceForm


class CountryAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', )
    ordering = ['name']


class StorageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ['name']


class FileStorageGeneralAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('time', 'used', 'free', 'percentage')
    ordering = ['time']

    def percentage(self, obj):
        return "{0:.2f}%".format((obj.used / (obj.used+obj.free)) * 100)


class PortAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'country', 'latitude', 'longitude', 'source')
    ordering = ['name']


class PositionUncertaintyAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'table_code', 'source')
    ordering = ['name']


class TimeUncertaintyAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'source')
    ordering = ['name']

class TimeSourceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'definition')
    ordering = ['name']

class PositionSourceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display= ('name', 'definition')
    ordering = ['name']

class PreservationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ['name']


class SpeciesClassificationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('phylum', 'class2', 'order', 'family', 'genus', 'species')
    ordering = ['phylum']


class SampleContentAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('type', 'species_classification', 'description')
    ordering = ['type']


class SampleAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'event', 'storage', 'preservation', 'owner', 'contents', 'destination')
    ordering = ['code']


class PersonAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name_title', 'name_first', 'name_middle', 'name_last', 'project_list', 'organisation_list')
    ordering = ['name_last']

    def project_list(self, obj):
        projects = obj.project.all()

        return ",".join([project.title for project in projects])

    def organisation_list(self, obj):
        organisations = obj.organisation.all()

        return ",".join([organisation.name for organisation in organisations])


class OrganisationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'address', 'country')
    ordering = ['name']


class DataAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('event', 'project', 'storage_location', 'checked')
    ordering = ['event']


class FilesStorageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('relative_path', 'kilobytes')

    ordering = ['relative_path']


class StorageCrateAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'location', 'description', 'comment')
    ordering = ['name']


class NetworkHostAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('ip', 'hostname', 'location', 'comment')
    ordering = ['ip']


class PlatformTypeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'definition', 'source')
    ordering = ['name']


class DeviceTypeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('url', 'code', 'name', 'definition', 'version', 'deprecated', 'date', 'source')
    ordering = ['name']


class PlatformAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'platformtype')
    ordering = ['name']


class ShipAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'imo', 'callsign')
    ordering = ['name']


class ParentDeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'definition')
    ordering = ['name']

class MessageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'subject', 'message', 'person')
    ordering = ['-date_time']

admin.site.register(main.models.Ship, ShipAdmin)
admin.site.register(main.models.StationType, StationTypeAdmin)
admin.site.register(main.models.ChildDevice, ChildDeviceAdmin)
admin.site.register(main.models.DeviceType, DeviceTypeAdmin)
admin.site.register(main.models.ParentDevice, ParentDeviceAdmin)
admin.site.register(main.models.Project, ProjectAdmin)
admin.site.register(main.models.Event, EventAdmin)
admin.site.register(main.models.EventActionDescription, EventActionDescriptionAdmin)
admin.site.register(main.models.EventAction, EventActionAdmin)
admin.site.register(main.models.Station, StationAdmin)
admin.site.register(main.models.Leg, LegAdmin)
admin.site.register(main.models.EventReport, EventReportAdmin)
admin.site.register(main.models.Country, CountryAdmin)
admin.site.register(main.models.Storage, StorageAdmin)
admin.site.register(main.models.FilesStorageGeneral, FileStorageGeneralAdmin)
admin.site.register(main.models.Port, PortAdmin)
admin.site.register(main.models.PositionUncertainty, PositionUncertaintyAdmin)
admin.site.register(main.models.TimeUncertainty, TimeUncertaintyAdmin)
admin.site.register(main.models.TimeSource, TimeSourceAdmin)
admin.site.register(main.models.PositionSource, PositionSourceAdmin)
admin.site.register(main.models.Preservation, PreservationAdmin)
admin.site.register(main.models.SpeciesClassification, SpeciesClassificationAdmin)
admin.site.register(main.models.SampleContent, SampleContentAdmin)
admin.site.register(main.models.Sample, SampleAdmin)
admin.site.register(main.models.Person, PersonAdmin)
admin.site.register(main.models.Organisation, OrganisationAdmin)
admin.site.register(main.models.Data, DataAdmin)
admin.site.register(main.models.FilesStorage, FilesStorageAdmin)
admin.site.register(main.models.StorageCrate, StorageCrateAdmin)
admin.site.register(main.models.NetworkHost, NetworkHostAdmin)
admin.site.register(main.models.Platform, PlatformAdmin)
admin.site.register(main.models.PlatformType, PlatformTypeAdmin)
admin.site.register(main.models.Message, MessageAdmin)

ADMIN_SITE_TITLE = 'Ace Data Admin'
ADMIN_SITE_HEADER = 'ACE Data Administration'

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER
