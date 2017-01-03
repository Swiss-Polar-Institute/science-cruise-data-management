import django.utils
from django.contrib import admin
from django.utils.encoding import force_text

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


class SamplingMethodFilter(OutcomeReportFilter):
    title = "Sampling method"
    parameter_name = "sampling_method"
    template = "admin/options_filter_samplingmethod.html"

    def queryset(self, request, queryset):
        if self.value() is not None and self.value() != '':
            return queryset.filter(parent_device__id=self.value())
        else:
            return queryset

    def lookups(self, request, model_admin):
        parent_devices = main.models.ParentDevice.objects.all().order_by('name')

        filter_lookup = []
        for parent_device in parent_devices:
            filter_lookup.append((parent_device.id, parent_device.name))

        return tuple(filter_lookup)
