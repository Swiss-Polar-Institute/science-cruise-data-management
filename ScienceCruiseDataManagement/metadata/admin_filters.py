import django.utils
from django.contrib import admin
from django.utils.encoding import force_text
from django.forms.models import model_to_dict
import metadata.models
from main.admin_filters import OptionFilter


class ParameterFilter(OptionFilter):
    title = "Parameter"
    parameter_name = "parameter"
    template = "admin/options_filter_parameter.html"

    def filter(self, request, queryset):
        return queryset.filter(id=self.value())

    def lookups(self, request, model_admin):
        return self._prepare_filter_lookups(metadata.models.Parameter, 'topic')


class ProjectFilter(OptionFilter):
    title = "Project"
    parameter_name = "project"
    template = "admin/options_filter_metadata_entry_project.html"

    def filter(self, request, queryset):
        return queryset.filter(id=self.value())

    def lookups(self, request, model_admin):
        metadata_entries = metadata.models.MetadataEntry.objects.all().order_by('project__short_name')

        filter_lookup = []
        for entry in metadata_entries:
            projects = entry.expedition_project.all()
            for project in projects:
                filter_lookup.append((project.id, project.title))

        return tuple(filter_lookup)
