import django.utils
from django.contrib import admin
from django.utils.encoding import force_text
from django.forms.models import model_to_dict
import main.models


class OptionFilter(admin.SimpleListFilter):
    def __init__(self, request, params, model, model_admin):
        if self.parameter_name in params:
            request.session[self.parameter_name] = params[self.parameter_name]
            self._value = django.utils.http.urlunquote(params[self.parameter_name])
        elif self.parameter_name in request.session:
            self._value = django.utils.http.urlunquote(request.session[self.parameter_name])
        else:
            self._value = None

        super(OptionFilter, self).__init__(request, params, model, model_admin)

    def value(self):
        if self._value == '':
            return None
        else:
            return self._value

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'display': 'All',
        }
        for lookup, title in self.lookup_choices:
            query_string = "{}={}".format(self.parameter_name, {self.parameter_name: lookup})
            yield {
                'selected': self.value() == force_text(lookup),
                'id': lookup,
                'display': title,
            }

    def _prepare_filter_lookups(self, model, field, query_by_id=True):
        objects = model.objects.all().order_by(field)

        filter_lookup = []
        filter_values = []
        for object in objects:
            dict_of_model = model_to_dict(object)
            if dict_of_model[field] not in filter_values:
                if query_by_id:
                    id=dict_of_model['id']
                else:
                    id=dict_of_model[field]

                filter_lookup.append((id, dict_of_model[field]))
                filter_values.append(dict_of_model[field])

        return tuple(filter_lookup)


class OutcomeReportFilter(OptionFilter):
    title = "Outcome"
    parameter_name = "outcome"
    template = "admin/options_filter_outcome.html"

    def lookups(self, request, model_admin):
        return main.models.Event.type_choices

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(outcome=self.value())
        else:
            return queryset


class EmailLegFilter(OptionFilter):
    title = "Leg"
    parameter_name = "leg"
    template = "admin/options_mail_leg.html"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(person__leg__id=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        legs = main.models.Leg.objects.all().order_by('number')

        filter_lookup = []
        for leg in legs:
            filter_lookup.append((leg.id, leg.number))

        return tuple(filter_lookup)


class StationReportFilter(OptionFilter):
    title = "Station"
    parameter_name = "station"
    template = "admin/options_filter_station.html"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(station__id=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        stations = main.models.Station.objects.all().order_by('name')

        filter_lookup = []
        for station in stations:
            filter_lookup.append((station.id, station.name))

        return tuple(filter_lookup)


class SamplingMethodFilter(OptionFilter):
    title = "Sampling method"
    parameter_name = "sampling_method"
    template = "admin/options_filter_samplingmethod.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(sampling_method__id=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        sampling_methods = main.models.SamplingMethod.objects.all().order_by('name')

        filter_lookup = []
        for sampling_method in sampling_methods:
            filter_lookup.append((sampling_method.id, sampling_method.name))

        return tuple(filter_lookup)


class ProjectFilter(OptionFilter):
    title = "Project"
    parameter_name = "project"
    template = "admin/options_filter_project.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(project__id=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(main.models.Project, 'title', query_by_id=True)


class SampleContentsFilter(OptionFilter):
    title = "Contents"
    parameter_name = "sample_contents"
    template = "admin/options_filter_sample_contents.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(contents=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(main.models.Sample, 'contents', query_by_id=False)


class TypeOfStorageFilter(OptionFilter):
    title = "Type of Storage"
    parameter_name = "type_of_storage"
    template = "admin/options_filter_type_of_storage.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(storage_type=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(main.models.Sample, 'storage_type', query_by_id=False)


class StorageLocationFilter(OptionFilter):
    title = "Storage location"
    parameter_name = "storage_location"
    template = "admin/options_filter_storage_location.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(storage_location=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(main.models.Sample, 'storage_location', query_by_id=False)


class OffloadingPortFilter(OptionFilter):
    title = "Offloading port"
    parameter_name = "offloading_port"
    template = "admin/options_filter_offloading_port.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(offloading_port=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(main.models.Sample, 'offloading_port', query_by_id=False)


class EventFilter(OptionFilter):
    title = "Event"
    parameter_name = "event"
    template = "admin/options_filter_event.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(event_id=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(main.models.Sample, 'event', query_by_id=False)
