import import_export
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm

import main.lookups
import main.models
import main.utils
from main.admin_filters import OutcomeReportFilter, StationReportFilter,\
    SamplingMethodFilter, ProjectFilter, SampleContentsFilter, TypeOfStorageFilter, StorageLocationFilter,\
    OffloadingPortFilter, EventFilter


class ProjectsStartsWithLetter(admin.SimpleListFilter):
    title = "Projects starts with A"
    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        return (('a', 'Starts with A'),
                ('b', 'Starts with B'))

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(name__startswith=self.value())
        else:
            return queryset


class MissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'institution', 'description')
    ordering = ['name']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'alternative_title', 'principal_investigator', 'abstract')
    list_filter = (ProjectsStartsWithLetter,)
    ordering = ['number']


class ReadOnlyIfUserCantChangeEvents:
    def get_readonly_fields(self, request, obj=None):
        if not main.utils.can_user_change_events(request.path, request.user):
            fields_from_model = []

            # Here we want the fields of the model but without the 'related_field'.
            # E.g. if another model had a foreign key to this object with a 'related_name'
            # this appeared here but because it's not in this form the template
            # raised an exception (as it was included)
            for field in self.model._meta.get_fields(include_parents=False):
                if hasattr(self.model, field.name) \
                        and not hasattr(field, 'related_name'):
                    fields_from_model.append(field.name)

            # Outcome can always be changed (even by users who can't change the events)
            if 'outcome' in fields_from_model:
                fields_from_model.remove("outcome")
            return fields_from_model

        return []


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


class EventActionResource(import_export.resources.ModelResource):
    event = import_export.fields.Field(column_name='event', attribute='event')

    sampling_method = import_export.fields.Field(
        column_name='sampling_method',
        attribute='sampling_method',
        widget=import_export.widgets.ForeignKeyWidget(main.models.SamplingMethod, 'name')
    )

    type = import_export.fields.Field(column_name='type', attribute='type')

    description = import_export.fields.Field(
        column_name='description',
        attribute='description',
        widget=import_export.widgets.ForeignKeyWidget(main.models.EventActionDescription, 'name')
    )

    time = import_export.fields.Field(column_name='time', attribute='type')

    time_source =  import_export.fields.Field(
        column_name='time_source',
        attribute='time_source',
        widget=import_export.widgets.ForeignKeyWidget(main.models.TimeSource, 'name')
    )

    time_uncertainty = import_export.fields.Field(
        column_name='time_uncertainty',
        attribute='time_uncertainty',
        widget=import_export.widgets.ForeignKeyWidget(main.models.TimeUncertainty, 'name')
    )

    latitude = import_export.fields.Field(column_name='latitude', attribute='latitude')

    longitude = import_export.fields.Field(column_name='longitude', attribute='longitude')

    position_source = import_export.fields.Field(
        column_name='position_source',
        attribute='position_source',
        widget=import_export.widgets.ForeignKeyWidget(main.models.PositionSource, 'name')
    )

    position_uncertainty =import_export.fields.Field(
        column_name='position_uncertainty',
        attribute='position_uncertainty',
        widget=import_export.widgets.ForeignKeyWidget(main.models.PositionUncertainty, 'name')
    )

    water_depth = import_export.fields.Field(
        column_name='water_depth',
        attribute='water_depth'
    )

    general_comments = import_export.fields.Field(
        column_name='general_comments',
        attribute='general_comments'
    )

    data_source_comments = import_export.fields.Field(
        column_name='data_source',
        attribute='data_source'
    )

    class Meta:
        fields = ('event', 'sampling_method', 'type', 'description', 'time', 'time_source', 'time_uncertainty', 'latitude', 'longitude', 'position_source', 'position_uncertainty', 'water_depth', 'general_comments', 'data_source_comments', )
        export_order = fields


class EventActionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventActionForm, self).__init__(*args, **kwargs)
        # filter out closed events

        if self._adding_new_event_action():
            # This is to only show the open events when adding a new EventAction
            filter_open_events = self._filter_open_events()
            filter_success_failure = self._filter_event_success_or_failure()
            self.fields['event'].queryset = main.models.Event.objects.filter(filter_open_events).filter(filter_success_failure).order_by('-number')

    def _adding_new_event_action(self):
        # Returns True if the user is adding an event (instead of modifying it)
        # The reason is that we want to show all the events (and not only the open ones) if
        # the user is trying to modify an eventAction. When adding we only show the
        # ones that the user should select.
        #return len(self.fields) == 0
        return not self.instance.id

    def _filter_event_success_or_failure(self):
        filter_query = Q(outcome='Success') | Q(outcome='Failure')

        return filter_query

    def _filter_open_events(self):
        filter_query = Q(number=0) # Impossible with OR will be the rest

        for open_event_id in self._open_event_numbers():
                filter_query = filter_query | Q(number=open_event_id)

        return filter_query

    def _action_finished(self, event_action_id, event_number):
        event_actions_instant = main.models.EventAction.objects.filter(
                                Q(id=event_action_id) & Q(type="TINSTANT"))

        if len(event_actions_instant) > 0:
            return True

        event_actions = main.models.EventAction.objects.filter(Q(event=event_number) & Q(type="TENDS"))

        if len(event_actions) > 0:
            # There is an TENDS event so it's finished
            return True

        return False

    def _event_not_opened(self, event_id):
        other_events = main.models.EventAction.objects.filter(Q(event_id=event_id))

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


class EventActionAdmin(ReadOnlyIfUserCantChangeEvents, import_export.admin.ExportMixin, admin.ModelAdmin):
    #def description_2(self, obj):
    #    return obj.event_action_type.description

    #description_2.short_description = "Description"

    list_display = ('event', 'sampling_method', 'type', 'description', 'time', 'time_source', 'time_uncertainty', 'latitude', 'longitude', 'position_source', 'position_uncertainty', 'water_depth', 'general_comments', 'data_source_comments', 'created_by')
    ordering = ['-event_id', '-id']
    form = EventActionForm

    def created_by(self, obj):
        return main.utils.object_model_created_by(obj)

    def sampling_method(self, obj):
        return obj.event.sampling_method

    sampling_method.admin_order_field = "event__sampling_method"
    resource_class = EventActionResource


class EventActionDescriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'source')
    ordering = ['name']


class LegAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'start_time', 'start_port', 'end_time', 'end_port', 'active_leg')
    ordering = ['number']

    def active_leg(self, obj):
        return obj == main.models.Leg.current_active_leg()


class StationAdmin(ReadOnlyIfUserCantChangeEvents, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'type', 'latitude', 'longitude', 'leg', 'arrival_time', 'departure_time', 'time_source', 'time_uncertainty', 'position_source', 'position_uncertainty', 'water_depth', 'outcome', 'comment')
    ordering = ['-name']


# This is for the import_export
class EventResource(import_export.resources.ModelResource):
    number = import_export.fields.Field(column_name = 'number', attribute='number')

    sampling_method = import_export.fields.Field(
        column_name='smapling_method',
        attribute='sampling_method',
        widget=import_export.widgets.ForeignKeyWidget(main.models.SamplingMethod, 'name'))

    station = import_export.fields.Field(
        column_name='station',
        attribute='station',
        widget=import_export.widgets.ForeignKeyWidget(main.models.Station, 'name')
    )

    data = import_export.fields.Field(column_name = 'data', attribute='data')
    samples = import_export.fields.Field(column_name = 'samples', attribute='samples')
    outcome = import_export.fields.Field(column_name = 'outcome', attribute='outcome')

    class Meta:
        fields = ('number', 'smpling_method', 'station', 'data', 'samples', )
        export_order = fields


class EventReportResource(import_export.resources.ModelResource):
    number = import_export.fields.Field(column_name = 'number', attribute='number')

    station = import_export.fields.Field(column_name='station',
                                         attribute='station',
                                         widget=import_export.widgets.ForeignKeyWidget(main.models.Station, 'name'))

    sampling_method = import_export.fields.Field(column_name='sampling method',
                                               attribute='sampling_method',
                                               widget=import_export.widgets.ForeignKeyWidget(main.models.SamplingMethod, 'name'))

    start_time = import_export.fields.Field(column_name='start_time',
                                            attribute='start_time')

    start_latitude = import_export.fields.Field(column_name='start_latitude',
                                                attribute='start_latitude')

    start_longitude = import_export.fields.Field(column_name='start_longitude',
                                                 attribute='start_longitude')

    end_time = import_export.fields.Field(column_name='end_time',
                                          attribute='end_time')

    end_latitude = import_export.fields.Field(column_name='end_latitude',
                                              attribute='end_latitude')

    end_longitude = import_export.fields.Field(column_name='end_longitude',
                                               attribute='end_longitude')

    outcome = import_export.fields.Field(column_name ='outcome', attribute='outcome')

    # dehydrate_ is an import_eport.resources.ModelResource special prefix
    def dehydrate_start_time(self, event):
        return EventReportAdmin.start_time(event)

    def dehydrate_start_latitude(self, event):
        return EventReportAdmin.start_latitude(event)

    def dehydrate_start_longitude(self, event):
        return EventReportAdmin.start_longitude(event)

    def dehydrate_end_time(self, event):
        return EventReportAdmin.end_time(event)

    def dehydrate_end_latitude(self, event):
        return EventReportAdmin.end_latitude(event)

    def dehydrate_end_longitude(self, event):
        return EventReportAdmin.end_longitude(event)

    class Meta:
        fields = ('number', 'station', 'sampling_method', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude', 'outcome')
        export_order = fields


class EventReportAdmin(ReadOnlyIfUserCantChangeEvents, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'station_name', 'device_name', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude', 'outcome')
    list_filter = (SamplingMethodFilter, OutcomeReportFilter, StationReportFilter)

    resource_class = EventReportResource

    @classmethod
    def station_name(cls, obj):
        if obj.station is None:
            return "-"
        else:
            return obj.station.name

    @classmethod
    def device_name(cls, obj):
        return obj.sampling_method.name

    @classmethod
    def _get_event_action(cls, start_or_end, event_id, field):
        """ Returns the Event Action start (where type="TBEGNS" or "TINSTANT" and the EventId is
            the same as event_id
        """
        if start_or_end == "start":
            start_or_end = main.models.EventAction.tbegin()
        elif start_or_end == "end":
            start_or_end = main.models.EventAction.tends()
        else:
            assert False

        result = main.models.EventAction.objects.filter((Q(type=start_or_end) | Q(type="TINSTANT")) & Q(event_id=event_id))
        if len(result) > 0:
            return getattr(result[0], field)
        else:
            return None

    @classmethod
    def _get_event_action_start(cls, event_id, field):
        return EventReportAdmin._get_event_action('start', event_id, field)

    @classmethod
    def _get_event_action_end(cls, event_id, field):
        return EventReportAdmin._get_event_action('end', event_id, field)

    @classmethod
    def start_time(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'time')

    @classmethod
    def start_latitude(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'latitude')

    @classmethod
    def start_longitude(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'longitude')

    @classmethod
    def end_time(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'time')

    @classmethod
    def end_latitude(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'latitude')

    @classmethod
    def end_longitude(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'longitude')


class EventAdmin(ReadOnlyIfUserCantChangeEvents, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'sampling_method', 'station', 'data', 'samples', 'outcome', 'created_by')
    ordering = ['-number']

    # used for the import_export
    resource_class = EventResource

    def created_by(self, obj):
        return main.utils.object_model_created_by(obj)

    # This is to have a default value on the foreign key
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "leg":
            kwargs["queryset"] = main.models.Leg.objects.filter(name="Leg 1")
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def get_fields(self, request, obj=None):
        fields = list(self.list_display)

        # never shown, it's the primary key
        fields.remove('number')

        # It doesn't exist in the database, it's only in the list
        fields.remove('created_by')


        return tuple(fields)

    form = EventForm


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
    list_display = ('name',) # leave comma here for tuple
    ordering = ['name']


class IslandAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'mid_lat', 'mid_lon')
    ordering = ['name']


class IslandLandingsAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('island', 'person', 'date')
    ordering = ['island']


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
    list_display = ('type', 'description')
    ordering = ['type']


class SampleForm(ModelForm):
    class Meta:
        model = main.models.Sample
        fields = '__all__'


class SampleAdmin(ReadOnlyIfUserCantChangeEvents, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_type', 'storage_location', 'offloading_port', 'destination', 'ship', 'mission', 'leg', 'project', 'julian_day', 'event', 'pi_initials', 'preservation', 'file', 'specific_contents')
    fields = list_display
    ordering = ['expedition_sample_code']
    readonly_fields = ('expedition_sample_code', )
    list_filter = (ProjectFilter, SampleContentsFilter, TypeOfStorageFilter, StorageLocationFilter, OffloadingPortFilter, EventFilter)
    form = SampleForm


class ImportedFileAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ("file_name", "date_imported")
    ordering = ['file_name']


class PersonAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name_title', 'name_first', 'name_middle', 'name_last', 'project_list', 'organisation_list', 'principal_investigator','leg_list')
    ordering = ['name_last']

    def project_list(self, obj):
        projects = obj.project.all()

        return ",".join([project.title for project in projects])

    def organisation_list(self, obj):
        organisations = obj.organisation.all()

        return ",".join([organisation.name for organisation in organisations])

    def leg_list(self, obj):
        legs = obj.leg.all()

        return ",".join([str(leg.number) for leg in legs])


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
    list_display = ('name', 'platform_type')
    ordering = ['name']


class ShipAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'imo', 'callsign')
    ordering = ['name']


class SamplingMethodAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'definition')
    ordering = ['name']


class MessageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'subject', 'message', 'person')
    ordering = ['-date_time']


class TimeChangeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_changed_utc', 'difference_to_utc_after_change')
    ordering = ['date_changed_utc']


admin.site.register(main.models.Mission, MissionAdmin)
admin.site.register(main.models.Ship, ShipAdmin)
admin.site.register(main.models.StationType, StationTypeAdmin)
admin.site.register(main.models.ChildDevice, ChildDeviceAdmin)
admin.site.register(main.models.DeviceType, DeviceTypeAdmin)
admin.site.register(main.models.SamplingMethod, SamplingMethodAdmin)
admin.site.register(main.models.Project, ProjectAdmin)
admin.site.register(main.models.Event, EventAdmin)
admin.site.register(main.models.EventActionDescription, EventActionDescriptionAdmin)
admin.site.register(main.models.EventAction, EventActionAdmin)
admin.site.register(main.models.Station, StationAdmin)
admin.site.register(main.models.Leg, LegAdmin)
admin.site.register(main.models.EventReport, EventReportAdmin)
admin.site.register(main.models.Country, CountryAdmin)
admin.site.register(main.models.Island, IslandAdmin)
admin.site.register(main.models.IslandLandings, IslandLandingsAdmin)
admin.site.register(main.models.Storage, StorageAdmin)
admin.site.register(main.models.FilesStorageGeneral, FileStorageGeneralAdmin)
admin.site.register(main.models.Port, PortAdmin)
admin.site.register(main.models.PositionUncertainty, PositionUncertaintyAdmin)
admin.site.register(main.models.TimeUncertainty, TimeUncertaintyAdmin)
admin.site.register(main.models.TimeSource, TimeSourceAdmin)
admin.site.register(main.models.PositionSource, PositionSourceAdmin)
admin.site.register(main.models.Preservation, PreservationAdmin)
admin.site.register(main.models.SpeciesClassification, SpeciesClassificationAdmin)
admin.site.register(main.models.Sample, SampleAdmin)
admin.site.register(main.models.ImportedFile, ImportedFileAdmin)
admin.site.register(main.models.Person, PersonAdmin)
admin.site.register(main.models.Organisation, OrganisationAdmin)
admin.site.register(main.models.Data, DataAdmin)
admin.site.register(main.models.FilesStorage, FilesStorageAdmin)
admin.site.register(main.models.StorageCrate, StorageCrateAdmin)
admin.site.register(main.models.NetworkHost, NetworkHostAdmin)
admin.site.register(main.models.Platform, PlatformAdmin)
admin.site.register(main.models.PlatformType, PlatformTypeAdmin)
admin.site.register(main.models.Message, MessageAdmin)
admin.site.register(main.models.TimeChange, TimeChangeAdmin)

ADMIN_SITE_TITLE = 'Ace Data Admin'
ADMIN_SITE_HEADER = 'ACE Data Administration'

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER
