import import_export
import time
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm, ModelChoiceField
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

import main.lookups
import main.models
import main.utils
from main.admin_filters import OutcomeFilter, StationReportFilter, ProjectReportFilter, \
    SamplingMethodFilter, SampleContentsFilter, TypeOfStorageFilter, StorageLocationFilter,\
    OffloadingPortFilter, EventFilter, LegFilter, DeviceTypeFilter, ContactFilter, ProjectFilter, UsedLegFilter,\
    LegNumberFilter, StationTypeFilter, PrincipalInvestigatorFilter, PersonLegFilter, RoleFilter,\
    OtherFilters
import main.utils_event
import ctd.admin
import ctd.models

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

class MissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'institution', 'description')
    ordering = ['name']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'alternative_title', 'principal_investigator', 'abstract', 'sampling_methods_list', 'mission')
    ordering = ['number']

    def sampling_methods_list(self, obj):
        sampling_methods = obj.sampling_methods.all()

        return ", ".join([sampling_method.name for sampling_method in sampling_methods])

    filter_vertical = ('sampling_methods', )


class ReadOnlyIfUserCantChange:
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


class SpecificDeviceForm(ModelForm):
    # The AutoCompleteSelectField is disabled because this widget didn't work correctly
    # type_of_device = AutoCompleteSelectField(lookup_class=main.lookups.DeviceTypeLookup, allow_new=False)

    class Meta:
        model = main.models.SpecificDevice
        fields = '__all__'


class EventForm(ModelForm):
    class Meta:
        model = main.models.Event
        exclude = ('specific_devices', )
        # 'specific_device' is not here on purpose, for now


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

    time_source = import_export.fields.Field(
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


class EventNumberAndSamplingMethod(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}-{}".format(obj.number, obj.sampling_method.name)


class EventActionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventActionForm, self).__init__(*args, **kwargs)
        # filter out closed events

        if self._adding_new_event_action():
            # This is to only show the open events when adding a new EventAction
            open_events = EventActionForm.open_events_queryset()
            event_number_and_sampling_method = EventNumberAndSamplingMethod(queryset=open_events)
            self.fields['event'] = event_number_and_sampling_method
        else:
            event_number_and_sampling_method = EventNumberAndSamplingMethod(queryset=main.models.Event.objects.all().order_by('-number'))
            self.fields['event'] = event_number_and_sampling_method

        rel_model = self.Meta.model
        rel = rel_model._meta.get_field('event').remote_field
        self.fields['event'].widget = RelatedFieldWidgetWrapper(self.fields['event'].widget, rel, admin.site,
                                                                can_add_related=True, can_change_related=True)

    @staticmethod
    def open_events_queryset():
        filter_open_events = main.utils.filter_open_events()
        filter_success_failure = main.utils.filter_events_success_or_failure()
        open_events = main.models.Event.objects.filter(filter_open_events).filter(filter_success_failure).order_by('-number')

        return open_events

    def _adding_new_event_action(self):
        # Returns True if the user is adding an event (instead of modifying it)
        # The reason is that we want to show all the events (and not only the open ones) if
        # the user is trying to modify an eventAction. When adding we only show the
        # ones that the user should select.
        #return len(self.fields) == 0
        return not self.instance.id


    class Meta:
        model = main.models.EventAction
        fields = '__all__'


class EventActionAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('event', 'sampling_method', 'type', 'description', 'time', 'time_source', 'time_uncertainty', 'latitude', 'longitude', 'position_source', 'position_uncertainty', 'water_depth', 'general_comments', 'data_source_comments')
    ordering = ['-event_id', '-id']

    form = EventActionForm
    search_fields = ('event__number', )

    def created_by(self, obj):
        return main.utils.object_model_created_by(obj)

    def sampling_method(self, obj):
        return obj.event.sampling_method

    def response_add(self, request, obj, post_url_continue=None):
        if request.GET is not None and "from_eventreport" in request.GET:
            return redirect("/admin/main/eventreport")
        else:
            return super(EventActionAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if request.GET is not None and "from_eventreport" in request.GET:
            return redirect("/admin/main/eventreport")
        else:
            return super(EventActionAdmin, self).response_add(request, obj)

    sampling_method.admin_order_field = "event__sampling_method"
    resource_class = EventActionResource


class EventActionDescriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'source')
    ordering = ['name']


class LegAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'start_time', 'start_port', 'end_time', 'end_port', 'active_leg')
    ordering = ['number']

    def active_leg(self, obj):
        return obj == main.models.Leg.current_active_leg()


class CtdCastAdmin(admin.ModelAdmin):
    list_display = ('ctd_cast_number', 'event_number', 'leg_number', 'ctd_operator', 'ctd_file_name', 'ice_coverage', 'sea_state', 'water_depth', 'surface_temperature', 'surface_salinity', 'comments')
    ordering = ['ctd_cast_number', 'event_number', 'leg_number']
    search_fields = ['ctd_cast_number']
    list_filter = (LegNumberFilter, )

    inlines = [ctd.admin.CtdBottleTriggerInLine]


class TmrCastAdmin(admin.ModelAdmin):
    list_display = ('tmr_cast_number', 'event_number', 'leg_number')
    ordering = ['tmr_cast_number', 'event_number', 'leg_number']


class StationAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'type', 'latitude', 'longitude', 'leg', 'arrival_time', 'departure_time', 'time_source', 'time_uncertainty', 'position_source', 'position_uncertainty', 'water_depth', 'outcome', 'comment')
    ordering = ['-name']
    list_filter = (StationTypeFilter, LegFilter, OutcomeFilter)


class ProposedStationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'type', 'latitude', 'longitude','comment')
    ordering = ['name']


# This is for the import_export
class EventResource(import_export.resources.ModelResource):
    number = import_export.fields.Field(column_name = 'number', attribute='number')

    sampling_method = import_export.fields.Field(
        column_name='sampling_method',
        attribute='sampling_method',
        widget=import_export.widgets.ForeignKeyWidget(main.models.SamplingMethod, 'name'))

    station = import_export.fields.Field(
        column_name='station',
        attribute='station',
        widget=import_export.widgets.ForeignKeyWidget(main.models.Station, 'name')
    )

    data = import_export.fields.Field(column_name = 'data', attribute='data')
    samples = import_export.fields.Field(column_name = 'samples', attribute='samples')

    class Meta:
        fields = ('number', 'sampling_method', 'station', 'data', 'samples', )
        export_order = fields


class EventReportResource(import_export.resources.ModelResource):
    number = import_export.fields.Field(column_name='number', attribute='number')

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

    event_comments = import_export.fields.Field(column_name='event_comments',
                                                attribute='comments')
    # dehydrate_ is an import_eport.resources.ModelResource special prefix
    def dehydrate_start_time(self, event):
        return EventReportAdmin.start_time_(event)

    def dehydrate_start_latitude(self, event):
        return EventReportAdmin.start_latitude(event)

    def dehydrate_start_longitude(self, event):
        return EventReportAdmin.start_longitude(event)

    def dehydrate_end_time(self, event):
        return EventReportAdmin.end_time_(event)

    def dehydrate_end_latitude(self, event):
        return EventReportAdmin.end_latitude(event)

    def dehydrate_end_longitude(self, event):
        return EventReportAdmin.end_longitude(event)

    class Meta:
        fields = ('number', 'station', 'sampling_method', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude', 'outcome', 'event_comments')
        export_order = fields


class EventReportAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'station_name', 'device_name', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude', 'outcome', 'comments')
    list_filter = (SamplingMethodFilter, OutcomeFilter, StationReportFilter, ProjectReportFilter, OtherFilters, )
    search_fields = ('number',)

    resource_class = EventReportResource

    def __init__(self, *args, **kwargs):
        super(EventReportAdmin, self).__init__(*args, **kwargs)
        self._last_open_queryset = None
        self._last_open_queryset_time = 0

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
    def start_time_(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'time')

    @classmethod
    def end_time_(cls, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'time')

    def can_add_event_action(self, event):
        # Keeps results for one second to speed up the Report easily
        if time.time() - self._last_open_queryset_time > 1:
            self._last_open_queryset_time = time.time()
            self._last_open_queryset = EventActionForm.open_events_queryset()

        return event in self._last_open_queryset

    def start_time(self, obj):
        event_action_id = EventReportAdmin._get_event_action_start(obj.number, 'id')

        can_add_event_action = self.can_add_event_action(obj)

        if event_action_id is None and can_add_event_action:
            url = "/admin/main/eventaction/add/?event={}&type={}&from_eventreport=1".format(obj.number,
                                                                         main.models.EventAction.tbegin())
            url_instantaneous = "/admin/main/eventaction/add/?event={}&type={}&from_eventreport=1".format(obj.number,
                                                                         main.models.EventAction.tinstant())

            return '<a href="{}">Add start time</a> / <a href="{}">Instantaneous</a>'.format(url, url_instantaneous)
        elif event_action_id is None and not can_add_event_action:
            return "Change Event outcome to add a time"
        else:
            time = EventReportAdmin._get_event_action_start(obj.number, 'time')
            if time is not None:
                formatted_time = time.strftime("%Y-%m-%d&nbsp;%H:%M:%S")
            else:
                formatted_time = "-"
            url = "/admin/main/eventaction/{}/change/?from_eventreport=1".format(event_action_id)
            return mark_safe('<a href="{}">{}</a>'.format(url, formatted_time))

    start_time.allow_tags = True

    @classmethod
    def start_latitude(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'latitude')

    @classmethod
    def start_longitude(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'longitude')

    def end_time(self, obj):
        event_action_id = EventReportAdmin._get_event_action_end(obj.number, 'id')
        can_add_event_action = self.can_add_event_action(obj)

        time = EventReportAdmin._get_event_action_end(obj.number, 'time')

        if time is None and "Add start time" in self.start_time(obj):
            return "-"
        elif event_action_id is None and can_add_event_action:
            url = "/admin/main/eventaction/add/?event={}&type={}&from_eventreport=1".format(obj.number,
                                                                         main.models.EventAction.tends())
            return '<a href="{}">Add end time</a>'.format(url)
        elif event_action_id is None and not can_add_event_action:
            return "Change Event outcome to add a time"
        else:
            if time is not None:
                formatted_time = time.strftime("%Y-%m-%d&nbsp;%H:%M:%S")
            else:
                formatted_time = "-"

            url = "/admin/main/eventaction/{}/change/?from_eventreport=1".format(event_action_id)
            return mark_safe('<a href="{}">{}</a>'.format(url, formatted_time))

    end_time.allow_tags = True

    @classmethod
    def end_latitude(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'latitude')

    @classmethod
    def end_longitude(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'longitude')


class EventAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'sampling_method', 'station', 'data', 'samples', 'outcome', 'comments')
    ordering = ['-number']
    search_fields = ('number',)

    # used for the import_export
    resource_class = EventResource

    def created_by(self, obj):
        return main.utils.object_model_created_by(obj)

    # This is to have a default value on the foreign key
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "leg":
            kwargs["queryset"] = main.models.Leg.objects.filter(name="Leg 1")
        elif db_field.name == "sampling_method":
            kwargs["queryset"] = main.models.SamplingMethod.objects.exclude(validity="redundant").order_by("name")
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def get_fields(self, request, obj=None):
        fields = list(self.list_display)

        # never shown, it's the primary key
        fields.remove('number')

        # It doesn't exist in the database, it's only in the list
        if 'created_by' in fields:
            fields.remove('created_by')


        return tuple(fields)

    form = EventForm


class StationTypeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('type', 'description')
    ordering = ['type']


class SpecificDeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('type_of_device', 'full_name',  'shortened_name', 'description', 'sampling_method', 'directory_list', 'type_of_identifying_mark', 'identifying_mark', 'make', 'model', 'parent_list', 'platform_list', 'device_contact_list', 'leg_used_list', 'project_list', 'calibration_required', 'calibration_documents', 'calibration_comments', 'device_comments')
    list_filter = (DeviceTypeFilter, ContactFilter, ProjectFilter, UsedLegFilter,)

    #def device_type_name(self, obj):
     #   return obj.type_of_device.name

    # TODO: doesn't work here, check it again
    # ordering = ['device_type_name__name']

    def directory_list(self, obj):
        directories = obj.directory.all()

        return ", ".join([directory.destination_directory for directory in directories])

    def parent_list(self, obj):
        parents = obj.parent.all()

        result = ""
        for parent in parents:
            if result != "":
                result = result + ", "
            result = result + parent.type_of_device.full_name

        return result

    def platform_list(self, obj):
        platforms = obj.platform.all()

        result = ""
        for platform in platforms:
            if result != "":
                result = result + ", "
            result = result + platform.name

        return result

    def device_contact_list(self, obj):
        people = obj.device_contact.all()

        result = ""
        for person in people:
            if result != "":
                result = result + ", "
            result = result + person.name_first + ' ' + person.name_last

        return result

    def project_list(self, obj):
        projects = obj.project.all()

        return ", ".join([project.title for project in projects])

    def leg_used_list(self, obj):
        legs = obj.leg_used.all()

        return ", ".join([str(leg.number) for leg in legs])

    filter_vertical = ('directory',)

    #device_type_name.admin_order_field = 'device_type_name__name'
    form = SpecificDeviceForm

class DeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('full_name', 'shortened_name', 'description', 'main_device_type_list', 'instruments_list')
    ordering = ['full_name']

    filter_vertical = ('instruments',)

    def main_device_type_list(self, obj):
        main_devices = obj.main_device_type.all()

        result = ""
        for main_device in main_devices:
            if result != "":
                result = result + ", "
            result = result + main_device.name

        return result

    def instruments_list(self, obj):
        instruments = obj.instruments.all()

        return ", ".join([str(instrument) for instrument in instruments])

class CountryAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name',) # leave comma here for tuple
    ordering = ['name']


class IslandAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'mid_lat', 'mid_lon', 'island_group')
    ordering = ['name']


class IslandLandingsAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('island', 'person', 'date')
    ordering = ['island']
    search_fields = ('island__name', 'person__name_first', 'person__name_last')
    save_as = True


class StorageTypeAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'created_on', 'created_by')
    exclude = ('created_by',)
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


class SampleContentAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('type', 'description')
    ordering = ['type']


class SampleForm(ModelForm):
    class Meta:
        model = main.models.Sample
        fields = '__all__'


class SampleAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_type', 'storage_location', 'offloading_port', 'destination', 'ship', 'mission', 'leg', 'project', 'julian_day', 'event', 'pi_initials_str', 'preservation', 'file', 'specific_contents')
    fields = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_type', 'storage_location', 'offloading_port', 'destination', 'ship', 'mission', 'leg', 'project', 'julian_day', 'event', 'pi_initials', 'preservation', 'file', 'specific_contents')
    ordering = ['expedition_sample_code']
    readonly_fields = ('expedition_sample_code', )
    list_filter = (ProjectFilter, LegFilter, SampleContentsFilter, TypeOfStorageFilter, StorageLocationFilter, OffloadingPortFilter, EventFilter)
    search_fields = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_location', 'offloading_port', 'destination', 'julian_day', 'event__number', 'pi_initials__initials', 'preservation__name', 'file', 'specific_contents')
    form = SampleForm

    def pi_initials_str(self, obj):
        return f'{obj.pi_initials.name_first} {obj.pi_initials.name_last}'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('storage_type')
        queryset = queryset.prefetch_related('ship')
        queryset = queryset.prefetch_related('mission')
        queryset = queryset.prefetch_related('leg')
        queryset = queryset.prefetch_related('project')
        queryset = queryset.prefetch_related('event')
        queryset = queryset.prefetch_related('pi_initials')
        queryset = queryset.prefetch_related('pi_initials__organisation')
        queryset = queryset.prefetch_related('preservation')

        return queryset


class ImportedFileAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ("file_name", "date_imported")
    ordering = ['file_name']


class PersonAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name_title', 'name_first', 'name_middle', 'name_last', 'organisation_list', 'email_address', 'mailing_list_list')
    ordering = ['name_last']
    search_fields = ('name_first', 'name_middle', 'name_last')

    def organisation_list(self, obj):
        organisations = obj.organisation.all()

        return ", ".join([organisation.name for organisation in organisations])

    def mailing_list_list(self, obj):
        mailing_lists = obj.mailing_list.all()

        return ", ".join([mailing_list.name for mailing_list in mailing_lists])

class PersonRoleAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('person_name_last', 'project', 'role', 'principal_investigator', 'leg_list')
    ordering = ['person', 'project', 'leg']
    search_fields = ('person__name_first', 'person__name_last')
    list_filter = (LegFilter, ProjectFilter, RoleFilter)

    def person_name_last(self, obj):
        return "{}, {}".format(obj.person.name_last, obj.person.name_first)

    person_name_last.admin_order_field = "person__name_last"

    def leg_list(self, obj):
        legs = obj.leg.all()

        return ", ".join([str(leg.number) for leg in legs])


# This is for the import_export
class EmailResource(import_export.resources.ModelResource):
    person_name_first = import_export.fields.Field(
        column_name='person_name_first',
        attribute='person',
        widget=import_export.widgets.ForeignKeyWidget(main.models.Person, 'name_first'))

    person_name_last = import_export.fields.Field(
        column_name='person_name_last',
        attribute='person',
        widget=import_export.widgets.ForeignKeyWidget(main.models.Station, 'name_last')
    )

    email_address = import_export.fields.Field(column_name='email_address', attribute='email_address')
    webmail_password = import_export.fields.Field(column_name='webmail_password', attribute='webmail_password')
    server_password = import_export.fields.Field(column_name='server_password', attribute='server_password')

    class Meta:
        fields = ('person_name_first', 'person_name_last', 'email_address', 'webmail_password', 'server_password', )
        export_order = fields


class EmailAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('person_name_first', 'person_name_last', 'email_address', 'webmail_password', 'server_password')
    ordering = ['email_address']
    search_fields = ('email_address', )
    list_filter = (PersonLegFilter, )
    resource_class = EmailResource

    def person_name_first(self, obj):
        return obj.person.name_first

    def person_name_last(self, obj):
        return obj.person.name_last


class EmailOversizeNotifiedAdmin(admin.ModelAdmin):
    list_display = ('from_email', 'to_email_address', 'date_string', 'size_kb', 'subject', 'imap_uuid', 'added')

    def to_email_address(self, obj):
        return obj.to_email.email_address

    def size_kb(self, obj):
        return "{}".format(int(obj.size/1024))

class OrganisationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'country')
    ordering = ['name']


class RoleAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('role', 'description')
    ordering = ['role']
    search_fields = ('role',)


class FilesStorageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('relative_path', 'kilobytes')

    ordering = ['relative_path']


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
    list_display = ('name', 'code', 'short_name', 'uuid', 'country', 'platform_type', 'source', )
    ordering = ['name']


class ShipAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'imo', 'callsign')
    ordering = ['name']


class SamplingMethodAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'definition', 'directory_list', 'validity', 'date_validity_changed')
    ordering = ['name', 'validity']

    filter_vertical = ('directory',)

    def directory_list(self, obj):
        directories = obj.directory.all()

        return ", ".join([directory.destination_directory for directory in directories])


class MessageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'subject', 'message', 'person')
    ordering = ['-date_time']


class TimeChangeAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_changed_utc', 'date_changed_ship_time', 'difference_to_utc_after_change', 'data_source', 'comments')
    ordering = ['date_changed_utc']


class DepthAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'depth')
    ordering = ['-date_time']


class EventsConsistencyAdmin(admin.ModelAdmin):
    list_display = ('type', )

class EventsConsistencyAdminV2(admin.ModelAdmin):
    list_display = ('type', )


class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'other')
    ordering = ['name']


    def response_add(self, request, obj, post_url_continue=None):
        return redirect("/contacts")

    def response_change(self, request, obj):
        return redirect("/contacts")


class MeasurelandQualifierFlagsAdmin(admin.ModelAdmin):
    list_display = ('concept_id', 'preferred_label', 'alt_label', 'definition', 'modified', 'source')
    ordering = ('concept_id', )


# class EventsConsistencyAdmin(admin.ModelAdmin):
#     list_display = ('event_from_sample', 'project', 'samples_list', 'type')
#     ordering = ['-event_from_sample']
#
#     def samples_list(self, obj):
#         samples = obj.samples.all()
#
#         return ", ".join([str(sample) for sample in samples])


admin.site.register(main.models.Depth, DepthAdmin)
admin.site.register(main.models.Mission, MissionAdmin)
admin.site.register(main.models.Ship, ShipAdmin)
admin.site.register(main.models.StationType, StationTypeAdmin)
admin.site.register(main.models.SpecificDevice, SpecificDeviceAdmin)
admin.site.register(main.models.DeviceType, DeviceTypeAdmin)
admin.site.register(main.models.SamplingMethod, SamplingMethodAdmin)
admin.site.register(main.models.Project, ProjectAdmin)
admin.site.register(main.models.Event, EventAdmin)
admin.site.register(main.models.EventActionDescription, EventActionDescriptionAdmin)
admin.site.register(main.models.EventAction, EventActionAdmin)
admin.site.register(main.models.Station, StationAdmin)
admin.site.register(main.models.ProposedStation, ProposedStationAdmin)
admin.site.register(main.models.Leg, LegAdmin)
admin.site.register(main.models.EventReport, EventReportAdmin)
admin.site.register(main.models.Country, CountryAdmin)
admin.site.register(main.models.Island, IslandAdmin)
admin.site.register(main.models.IslandLandings, IslandLandingsAdmin)
admin.site.register(main.models.StorageType, StorageTypeAdmin)
admin.site.register(main.models.FilesStorageGeneral, FileStorageGeneralAdmin)
admin.site.register(main.models.Port, PortAdmin)
admin.site.register(main.models.PositionUncertainty, PositionUncertaintyAdmin)
admin.site.register(main.models.TimeUncertainty, TimeUncertaintyAdmin)
admin.site.register(main.models.TimeSource, TimeSourceAdmin)
admin.site.register(main.models.PositionSource, PositionSourceAdmin)
admin.site.register(main.models.Preservation, PreservationAdmin)
admin.site.register(main.models.Sample, SampleAdmin)
admin.site.register(main.models.ImportedFile, ImportedFileAdmin)
admin.site.register(main.models.Person, PersonAdmin)
admin.site.register(main.models.PersonRole, PersonRoleAdmin)
admin.site.register(main.models.Email, EmailAdmin)
admin.site.register(main.models.Organisation, OrganisationAdmin)
admin.site.register(main.models.FilesStorage, FilesStorageAdmin)
admin.site.register(main.models.NetworkHost, NetworkHostAdmin)
admin.site.register(main.models.Platform, PlatformAdmin)
admin.site.register(main.models.PlatformType, PlatformTypeAdmin)
admin.site.register(main.models.Message, MessageAdmin)
admin.site.register(main.models.TimeChange, TimeChangeAdmin)
admin.site.register(main.models.EmailOversizeNotified, EmailOversizeNotifiedAdmin)
admin.site.register(main.models.Device, DeviceAdmin)
admin.site.register(main.models.CtdCast, CtdCastAdmin)
admin.site.register(main.models.TmrCast, TmrCastAdmin)
admin.site.register(main.models.Role, RoleAdmin)
admin.site.register(main.models.EventsConsistency, EventsConsistencyAdmin)
admin.site.register(main.models.EventsConsistencyV2, EventsConsistencyAdminV2)
admin.site.register(main.models.ContactDetails, ContactDetailsAdmin)
admin.site.register(main.models.MeasurelandQualifierFlags, MeasurelandQualifierFlagsAdmin)

ADMIN_SITE_TITLE = 'Ace Data Admin'
ADMIN_SITE_HEADER = 'ACE Data Administration'

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER
