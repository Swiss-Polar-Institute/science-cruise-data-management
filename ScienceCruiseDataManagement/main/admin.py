from django.core.exceptions import ValidationError
from django.contrib import admin
from django.forms import ModelForm
import main.models
import import_export
from django.db.models import Q
import main.utils

# Register your models here.
# e.g. : admin.site.register(main.models.Data)


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
            return [f.name for f in self.model._meta.get_fields()]

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


class EventAdmin(ReadOnlyFields, import_export.admin.ImportExportModelAdmin):
    list_display = ('number', 'device', 'station')
    ordering = ['-number']
    # add for import-export: resource_class = EventResource


    # This is to have a default value on the foreign key
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "leg":
            kwargs["queryset"] = main.models.Leg.objects.filter(name="Leg 1")
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


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

        if 'event' in self.fields:
            # event is not in the fields if it's readonly
            self.fields['event'].queryset = main.models.Event.objects.all().filter(self._filter_open_events())

    def _filter_open_events(self):
        filter_query = Q(id=0) # Impossible with OR will be the rest

        for open_event_id in self._open_event_ids():
                filter_query = filter_query | Q(id=open_event_id)

        return filter_query

    def _action_finished(self, event_action_id, event_id):
        event_actions_instant = main.models.EventAction.objects.all().filter(
                                Q(id=event_action_id) & Q(type="TINSTANT"))

        if len(event_actions_instant) > 0:
            print("tinstant: event_action_id:", event_action_id, "event_id:", event_id)
            return True

        event_actions = main.models.EventAction.objects.all().filter(Q(event_id=event_id) & Q(type="TENDS"))

        if len(event_actions) > 0:
            print("tends: event_action_id:", event_action_id, "event_id:", event_id)
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

    def _open_event_ids(self):
        """ Returns the event IDs that have been started and not finished. """
        started_not_finished = []
        event_actions = main.models.EventAction.objects.all()
        events = main.models.Event.objects.all()
        open_event_ids = []

        # Adds events with TBEGNS and not finished
        for event_action in event_actions:
            if event_action.type == main.models.EventAction.tbegin():
                if not self._action_finished(event_action.id, event_action.event.id):
                    open_event_ids.append(event_action.event.id)

        for event in events:
            if self._event_not_opened(event.id):
                open_event_ids.append(event.id)

        return open_event_ids

    class Meta:
        model = main.models.EventAction
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        if len(data) == 0:
            # This can happen when all the fields are readonly
            return super(EventActionForm, self).clean()

        event_id = self.data['event']   # cleaned_data['event'] doesn't have this one
                                        # probably because the form filters it?
        type = data['type']

        tbegin = main.models.EventAction.tbegin()
        tends = main.models.EventAction.tends()
        tinstant = main.models.EventAction.tinstant()

        tbegin_text = main.models.EventAction.tbegin_text()
        tends_text = main.models.EventAction.tends_text()
        tinstant_text = main.models.EventAction.tinstant_text()


        if len(main.models.EventAction.objects.all().filter
                       (Q(event_id=event_id) & (Q(type=tends) |
                                                    (Q(type=tinstant)))))>0:
            raise ValidationError("Cannot add any EventAction because the Event has a '{}' or '{}'".format(tends_text,
                                                                                                      tinstant_text))

        if type == tends:
            if len(main.models.EventAction.objects.all().filter
                       (Q(event_id=event_id) & (Q(type=tends) | (Q(type=tinstant)))))>0:
                raise ValidationError("Cannot add {} because this Event already had '{}' or '{}'".format(tends, tends_text, tinstant_text))
            if len(main.models.EventAction.objects.all().filter
                       (Q(event_id=event_id) & (Q(type=tbegin)))) == 0:
                raise ValidationError("Cannot add '{}' because '{}' doesn't exist".format(tends_text, tbegin_text))

        return super(EventActionForm, self).clean()


class EventActionAdmin(ReadOnlyFields, import_export.admin.ExportMixin, admin.ModelAdmin):
    #def description_2(self, obj):
    #    return obj.event_action_type.description

    #description_2.short_description = "Description"

    list_display = ('id', 'event', 'type', 'description', 'description', 'time', 'time_source', 'time_uncertainty', 'latitude', 'longitude', 'position_source', 'position_uncertainty', 'water_depth', 'general_comments', 'data_source_comments')
    ordering = ['-event_id', '-id']
    form = EventActionForm

class EventActionDescriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'source')
    ordering = ['name']


class LegAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('number', 'start_time', 'start_port', 'end_time', 'end_port')
    ordering = ['number']


class StationAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'type', 'latitude', 'longitude', 'leg', 'arrival_time', 'departure_time', 'time_source', 'time_uncertainty', 'position_source', 'position_uncertainty', 'water_depth', 'comment')
    ordering = ['name']


class EventReportAdmin(ReadOnlyFields, import_export.admin.ExportMixin, admin.ModelAdmin):
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
    list_display = ('type', 'description')
    ordering = ['type']


class DeviceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name')
    ordering = ['code']


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
    list_display = ('code', 'name', 'latitude', 'longitude')
    ordering = ['code']


class PositionUncertaintyAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name')
    ordering = ['code']


class PositionSourceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'list', 'description')
    ordering = ['code']


class TimeUncertaintyAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'list', 'description')
    ordering = ['code']


class TimeSourceAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'list', 'description')
    ordering = ['code']


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


admin.site.register(main.models.Device, DeviceAdmin)
admin.site.register(main.models.StationType, StationTypeAdmin)
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
admin.site.register(main.models.PositionSource, PositionSourceAdmin)
admin.site.register(main.models.TimeUncertainty, TimeUncertaintyAdmin)
admin.site.register(main.models.TimeSource, TimeSourceAdmin)
admin.site.register(main.models.Preservation, PreservationAdmin)
admin.site.register(main.models.SpeciesClassification, SpeciesClassificationAdmin)
admin.site.register(main.models.SampleContent, SampleContentAdmin)
admin.site.register(main.models.Sample, SampleAdmin)
admin.site.register(main.models.Person, PersonAdmin)
admin.site.register(main.models.Organisation, OrganisationAdmin)
admin.site.register(main.models.Data, DataAdmin)
admin.site.register(main.models.FilesStorage, FilesStorageAdmin)
admin.site.register(main.models.StorageCrate, StorageCrateAdmin)


admin.site.site_header = 'ACE Data'
admin.site.site_title = 'ACE Data Admin'
admin.site.site_header = 'ACE Data Administration'