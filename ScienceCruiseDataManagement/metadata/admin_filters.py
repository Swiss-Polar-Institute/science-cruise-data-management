import django.utils
from django.contrib import admin
from django.utils.encoding import force_text
from django.forms.models import model_to_dict
import metadata.models


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

    def queryset(self, request, queryset):
        if self.value() is not None:
            return self.filter(request, queryset)
        else:
            return queryset

    def filter(self, request, queryset):
        raise NotImplementedError(
            "a from_string() method")

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


class ParameterFilter(OptionFilter):
    title = "Parameter"
    parameter_name = "parameter"
    template = "admin/options_filter_parameter.html"

    def filter(self, request, queryset):
        return queryset.filter(id=self.value())

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(metadata.models.Parameter, 'topic', query_by_id=True)