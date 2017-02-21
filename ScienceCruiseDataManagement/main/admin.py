import import_export
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.forms import ModelForm, ModelChoiceField
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

import main.lookups
import main.models
import main.utils
from main.admin_filters import OutcomeFilter, StationReportFilter,\
    SamplingMethodFilter, SampleContentsFilter, TypeOfStorageFilter, StorageLocationFilter,\
    OffloadingPortFilter, EventFilter, LegFilter, DeviceTypeFilter, ContactFilter, ProjectFilter, UsedLegFilter,\
    LegNumberFilter, StationTypeFilter, PrincipalInvestigatorFilter, PersonLegFilter
import main.utils_event


class MissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'institution', 'description')
    ordering = ['name']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'alternative_title', 'principal_investigator', 'abstract')
    ordering = ['number']


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


class EventNumberAndSamplingMethod(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}-{}".format(obj.number, obj.sampling_method.name)


class EventActionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventActionForm, self).__init__(*args, **kwargs)
        # filter out closed events

        if self._adding_new_event_action():
            # This is to only show the open events when adding a new EventAction
            # filter_open_events = self._filter_open_events()
            filter_open_events = self._filter_open_events()
            filter_success_failure = self._filter_events_success_or_failure()
            open_events = main.models.Event.objects.filter(filter_open_events).filter(filter_success_failure).order_by('-number')

            event_number_and_sampling_method = EventNumberAndSamplingMethod(queryset=open_events)
            self.fields['event'] = event_number_and_sampling_method
        else:
            event_number_and_sampling_method = EventNumberAndSamplingMethod(queryset=main.models.Event.objects.all().order_by('-number'))
            self.fields['event'] = event_number_and_sampling_method

        rel_model = self.Meta.model
        rel = rel_model._meta.get_field('event').rel
        self.fields['event'].widget = RelatedFieldWidgetWrapper(self.fields['event'].widget, rel, admin.site,
                                                                can_add_related=True, can_change_related=True)

    def _adding_new_event_action(self):
        # Returns True if the user is adding an event (instead of modifying it)
        # The reason is that we want to show all the events (and not only the open ones) if
        # the user is trying to modify an eventAction. When adding we only show the
        # ones that the user should select.
        #return len(self.fields) == 0
        return not self.instance.id

    def _filter_open_events(self):
        filter_query = Q(number=0)  # Impossible with OR will be the rest

        for open_event in main.models.OpenEvent.objects.all():
            filter_query = filter_query | Q(number=open_event.number)

        return filter_query


    def _filter_events_success_or_failure(self):
        filter_query = Q(outcome='Success') | Q(outcome='Failure')

        return filter_query

    class Meta:
        model = main.models.EventAction
        fields = '__all__'


class EventActionAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    #def description_2(self, obj):
    #    return obj.event_action_type.description

    #description_2.short_description = "Description"

    list_display = ('event', 'sampling_method', 'type', 'description', 'time', 'time_source', 'time_uncertainty', 'latitude', 'longitude', 'position_source', 'position_uncertainty', 'water_depth', 'general_comments', 'data_source_comments')
    ordering = ['-event_id', '-id']

    form = EventActionForm
    search_fields = ('event__number', )

    def created_by(self, obj):
        return main.utils.object_model_created_by(obj)

    def sampling_method(self, obj):
        return obj.event.sampling_method

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
    outcome = import_export.fields.Field(column_name = 'outcome', attribute='outcome')

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
    list_display = ('number', 'event_actions', 'station_name', 'device_name', 'start_time', 'start_latitude', 'start_longitude', 'end_time', 'end_latitude', 'end_longitude', 'outcome', 'comments')
    list_filter = (SamplingMethodFilter, OutcomeFilter, StationReportFilter)
    search_fields = ('number_',)

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
    def start_time_(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'time')

    @classmethod
    def end_time_(cls, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'time')

    def start_time(self, obj):
        event_action_id = EventReportAdmin._get_event_action_start(obj.number, 'id')
        if event_action_id is None:
            return "-"
        else:
            time = EventReportAdmin._get_event_action_start(obj.number, 'time')
            if time is not None:
                formatted_time = time.strftime("%Y-%m-%d&nbsp;%H:%M:%S")
            else:
                formatted_time = "-"

            url = "/admin/main/eventaction/{}".format(event_action_id)
            return '<a href="{}">{}</a>'.format(url, formatted_time)

    start_time.allow_tags = True

    @classmethod
    def start_latitude(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'latitude')

    @classmethod
    def start_longitude(cls, obj):
        return EventReportAdmin._get_event_action_start(obj.number, 'longitude')

    def end_time(self, obj):
        event_action_id = EventReportAdmin._get_event_action_end(obj.number, 'id')
        if event_action_id is None:
            return "-"
        else:
            time = EventReportAdmin._get_event_action_end(obj.number, 'time')
            if time is not None:
                formatted_time = time.strftime("%Y-%m-%d&nbsp;%H:%M:%S")
            else:
                formatted_time = "-"

            url = "/admin/main/eventaction/{}".format(event_action_id)
            return '<a href="{}">{}</a>'.format(url, formatted_time)

    end_time.allow_tags = True

    @classmethod
    def end_latitude(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'latitude')

    @classmethod
    def end_longitude(self, obj):
        return EventReportAdmin._get_event_action_end(obj.number, 'longitude')

    def event_actions(self, obj):
        return "<a href='/admin/main/eventaction/?q={}'>Click</a>".format(obj.number)
    event_actions.allow_tags = True


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
    list_display = ('type_of_device', 'description', 'type_of_identifying_mark', 'identifying_mark', 'make', 'model', 'parent_list', 'platform_list', 'device_contact_list', 'leg_used_list', 'project_list', 'calibration_required', 'calibration_documents', 'calibration_comments', 'device_comments')
    list_filter = (DeviceTypeFilter, ContactFilter, ProjectFilter, UsedLegFilter,)

    #def device_type_name(self, obj):
     #   return obj.type_of_device.name

    # TODO: doesn't work here, check it again
    # ordering = ['device_type_name__name']

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

        return ",".join([project.title for project in projects])

    def leg_used_list(self, obj):
        legs = obj.leg_used.all()

        return ",".join([str(leg.number) for leg in legs])


    #device_type_name.admin_order_field = 'device_type_name__name'
    form = SpecificDeviceForm

class DeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('full_name', 'shortened_name', 'description', 'main_device_type_list')
    ordering = ['full_name']

    def main_device_type_list(self, obj):
        main_devices = obj.main_device_type.all()

        result = ""
        for main_device in main_devices:
            if result != "":
                result = result + ", "
            result = result + main_device.name

        return result

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


class SampleAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_type', 'storage_location', 'offloading_port', 'destination', 'ship', 'mission', 'leg', 'project', 'julian_day', 'event', 'pi_initials', 'preservation', 'file', 'specific_contents')
    fields = list_display
    ordering = ['expedition_sample_code']
    readonly_fields = ('expedition_sample_code', )
    list_filter = (ProjectFilter, LegFilter, SampleContentsFilter, TypeOfStorageFilter, StorageLocationFilter, OffloadingPortFilter, EventFilter)
    search_fields = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_type', 'storage_location', 'offloading_port', 'destination', 'julian_day', 'event__number', 'pi_initials__initials', 'preservation__name', 'file', 'specific_contents')
    form = SampleForm


class ImportedFileAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ("file_name", "date_imported")
    ordering = ['file_name']


class PersonAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name_title', 'name_first', 'name_middle', 'name_last', 'project', 'onboard_role', 'organisation_list', 'email_address', 'principal_investigator','leg_list')
    ordering = ['name_last']
    search_fields = ('name_first', 'name_middle', 'name_last')
    list_filter = (LegFilter, ProjectFilter, PrincipalInvestigatorFilter, )

    def organisation_list(self, obj):
        organisations = obj.organisation.all()

        return ",".join([organisation.name for organisation in organisations])

    def leg_list(self, obj):
        legs = obj.leg.all()

        return ",".join([str(leg.number) for leg in legs])


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


class OnboardRoleAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('role', 'description')
    ordering = ['role']
    search_fields = ('role',)


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
    list_display = ('name', 'definition', 'validity', 'date_validity_changed')
    ordering = ['name', 'validity']


class MessageAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_time', 'subject', 'message', 'person')
    ordering = ['-date_time']


class TimeChangeAdmin(ReadOnlyIfUserCantChange, import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('date_changed_utc', 'difference_to_utc_after_change')
    ordering = ['date_changed_utc']


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
admin.site.register(main.models.Email, EmailAdmin)
admin.site.register(main.models.Organisation, OrganisationAdmin)
admin.site.register(main.models.Data, DataAdmin)
admin.site.register(main.models.FilesStorage, FilesStorageAdmin)
admin.site.register(main.models.StorageCrate, StorageCrateAdmin)
admin.site.register(main.models.NetworkHost, NetworkHostAdmin)
admin.site.register(main.models.Platform, PlatformAdmin)
admin.site.register(main.models.PlatformType, PlatformTypeAdmin)
admin.site.register(main.models.Message, MessageAdmin)
admin.site.register(main.models.TimeChange, TimeChangeAdmin)
admin.site.register(main.models.EmailOversizeNotified, EmailOversizeNotifiedAdmin)
admin.site.register(main.models.Device, DeviceAdmin)
admin.site.register(main.models.CtdCast, CtdCastAdmin)
admin.site.register(main.models.TmrCast, TmrCastAdmin)
admin.site.register(main.models.OnboardRole, OnboardRoleAdmin)

ADMIN_SITE_TITLE = 'Ace Data Admin'
ADMIN_SITE_HEADER = 'ACE Data Administration'

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER
