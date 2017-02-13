from django.shortcuts import render
from main.models import Project
from metadata.models import MetadataEntry
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
import types

class ProjectListView(ListView):
    model = Project
    template_name = "list_of_projects.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        return context


class MetadataEntryListView(ListView):
    model = MetadataEntry
    template_name = "list_of_metadata_entry.html"

    def get_context_data(self, **kwargs):
        context = super(MetadataEntryListView, self).get_context_data(**kwargs)
        return context


class MetadataEntryView(TemplateView):
    template_name = "metadata_entry.html"

    def get(self, request, *args, **kwargs):
        id = int(args[0])
        try:
            metadata_entry = MetadataEntry.objects.get(id=id)
        except ObjectDoesNotExist:
            pass

        rows = []

        rows.append(('ID', metadata_entry.entry_id))
        rows.append(('Title', metadata_entry.entry_title))

        # people = concatenate_entries(metadata_entry.personnel, ['name_first'])
        # rows.append(('Personnel', people))

        data_set_citation = concatenate_entries(metadata_entry.data_set_citation, ['dataset_title', 'dataset_creator'])
        rows.append(('Data set citation', data_set_citation))
        projects = concatenate_entries(metadata_entry.project, 'short_name')
        rows.append(('Projects', projects))

        return render(request, "metadata_entry.html", {'rows': rows})


def concatenate_entries(objects, fields):
    if isinstance(fields, str):
        fields = [fields]
    elif isinstance(fields, list):
        pass
    else:
        # Should be a string or a list
        assert False

    list_of_strings = []

    for object in objects.all():
        object_dictionary = model_to_dict(object)

        fields_data = []
        for field in fields:
            fields_data.append(object_dictionary[field])

        list_of_strings.append("-".join(fields_data))

    return ",".join(list_of_strings)