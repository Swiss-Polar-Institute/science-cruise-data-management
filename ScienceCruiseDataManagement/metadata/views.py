from django.shortcuts import render
from main.models import Project
from metadata.models import *
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

        #data_set_citation = concatenate_entries(metadata_entry.data_set_citation)
        rows.append(('Data set citation', render_object(metadata_entry.data_set_citation)))

        people = concatenate_entries(metadata_entry.personnel, ['person.__renderer__'])
        rows.append(('Personnel', people))

        parameters = concatenate_entries(metadata_entry.parameters)
        rows.append(('Parameters', parameters))

        sensor_names = concatenate_entries(metadata_entry.sensor_name)
        rows.append(('Sensor names', sensor_names))

        source_names = concatenate_entries(metadata_entry.source_name)
        rows.append(('Source names', source_names))

        temporal_coverages = concatenate_entries(metadata_entry.temporal_coverage)
        rows.append(('Temporal coverage', temporal_coverages))

        rows.append(('Data set progress', metadata_entry.data_set_progress))

        spatial_coverages = concatenate_entries(metadata_entry.spatial_coverage)
        rows.append(('Spatial coverage', spatial_coverages))

        locations = concatenate_entries(metadata_entry.location)
        rows.append(('Location', locations))

        data_resolutions = concatenate_entries(metadata_entry.data_resolution)
        rows.append(('Data resolution', data_resolutions))

        projects = concatenate_entries(metadata_entry.project)
        rows.append(('Projects', projects))

        rows.append(('Quality', metadata_entry.quality))

        rows.append(('Access constraints', metadata_entry.access_constraints))

        rows.append(('Use constraints', metadata_entry.use_constraints))

        rows.append(('Data set language', metadata_entry.data_set_language))

        rows.append(('Originating center', metadata_entry.originating_center))

        data_centers = concatenate_entries(metadata_entry.data_center)
        rows.append(('Data center', data_centers))

        distributions = concatenate_entries(metadata_entry.distribution)
        rows.append(('Distribution', distributions))

        rows.append(('Summary', metadata_entry.summary))

        rows.append(('Parent DIF', metadata_entry.parent_dif))

        idn_nodes = concatenate_entries(metadata_entry.idn_node)
        rows.append(('IDN node', idn_nodes))

        rows.append(('Metadata name', metadata_entry.metadata_name))

        rows.append(('Metadata version', metadata_entry.metadata_version))

        rows.append(('DIF creation date', metadata_entry.dif_creation_date))

        rows.append(('Last DIF revision date', metadata_entry.last_dif_revision_date))

        rows.append(('DIF revision history', metadata_entry.dif_revision_history))

        rows.append(('Future DIF review date', metadata_entry.future_dif_review_date))

        rows.append(('Private', metadata_entry.private))

        return render(request, "metadata_entry.html", {'rows': rows})


def get_attribute_from_field(object, field):
    # here field is a string and can contain ".": it will get resolved recursively
    assert isinstance(field, str)

    if "." in field:
        field_in_parts = field.split(".")
        field2 = getattr(object, field_in_parts[0])
        return get_attribute_from_field(field2, ".".join(field_in_parts[1:]))
    elif field == '__str__':
        return str(object)
    elif field == '__renderer__':
        return render_object(object)
    else:
        return str(getattr(object, field))

def object_to_html(object, specification_list):
    # specification_list: a list of specification
    # specification example: {'name_last': 'Name Last',
    #                         'show_if_empty': True
    #                        }
    pass

def render_object(object):
    if isinstance(object, Personnel):
        html = "TEST"
    elif isinstance(object, Person):
        html = object.name_first
    elif isinstance(object, DataSetCitation):
        html = ""
        if object.dataset_creator is not None:
            html += "Creator: " + str(object.dataset_creator) + "<br>"
        html += "Title: " + object.dataset_title + "<br>"

        if object.dataset_publisher is not None:
            html += "Publisher: " + object.dataset_publisher + "<br>"
        html += "Other citation details: " + object.other_citation_details + "<br>"

        if object.dataset_release_date is not None:
            html += "Release date: " + object.dataset_release_date.strftime("%Y-%m-%d") + "<br>"
        html += "Version: " + object.version
    else:
        assert False

    return html


def concatenate_entries(objects, fields='__str__'):
    if isinstance(fields, str):
        fields = [fields]
    elif isinstance(fields, list):
        pass
    else:
        # Should be a string or a list
        assert False

    list_of_strings = []

    for object in objects.all():
        fields_data = []
        for field in fields:
            fields_data.append(get_attribute_from_field(object, field))

        list_of_strings.append(" ".join(fields_data))

    return "<p>".join(list_of_strings)