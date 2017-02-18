from django.shortcuts import render
import datetime
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

        rows.append(('ID', render_object(metadata_entry.entry_id)))
        rows.append(('Title', render_object(metadata_entry.entry_title)))

        #data_set_citation = concatenate_entries(metadata_entry.data_set_citation)
        rows.append(('Data set citation', render_object(metadata_entry.data_set_citation)))

        #people = concatenate_entries(metadata_entry.personnel, ['person.__renderer__'])
        rows.append(('Personnel', render_object(metadata_entry.personnel.all())))

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

        rows.append(('Distribution', render_object(metadata_entry.distribution.all())))

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
    # specification list list of specifications
    #                         'output_string': 'Surname',
    #                         'show_if_empty': True
    #                        }
    output = ""

    for field in specification_list:
        line_output = field['output_string'] + ": "
        output_text = getattr(object, field['field_name'])

        is_empty = (output_text == "" or output_text is None)

        if is_empty and (field['show_if_empty'] is False):
            continue

        if is_empty and field['show_if_empty']:
            output_text = "-"

        output += line_output + render_object(output_text) + "<br>"

    return output

def render_queryset(qs, separator):
    output = []

    for object in qs:
        output.append(render_object(object))

    return separator.join(output)


def render_object(object, separator="<br>"):
    if isinstance(object, Person):
        html = "{} {}".format(object.name_first, object.name_last)
    elif isinstance(object, Distribution):
        specification_list = []

        specification_list.append({'field_name': 'distribution_format',
                                   'output_string': 'Format',
                                   'show_if_empty': True})

        specification_list.append({'field_name': 'distribution_size',
                                   'output_string': 'Size',
                                   'show_if_empty': True})

        specification_list.append({'field_name': 'distribution_media',
                                   'output_string': 'Media',
                                   'show_if_empty': True})

        specification_list.append({'field_name': 'fees',
                                   'output_string': 'Fees',
                                   'show_if_empty': True})

        html = object_to_html(object, specification_list)

    elif isinstance(object, models.QuerySet):
        html = render_queryset(object, separator)
    elif isinstance(object, DatasetRole):
        html = str(object)
    elif isinstance(object, Personnel):
        html = "Name: " + object.person.name_first + " " + object.person.name_last + " (DIF: " + render_object(object.dataset_role.all(), separator=", ") + "; Datacite: " + render_object(object.datacite_contributor_type.all(), separator=", ") + ")"
    elif isinstance(object, datetime.date):
        html = object.strftime("%Y-%m-%d")
    elif isinstance(object, str):
        html = object
    elif isinstance(object, DataSetCitation):
        specification_list = []

        specification_list.append({'field_name': 'dataset_creator',
                                   'output_string': 'Dataset Creator',
                                   'show_if_empty': True
                                   })
        specification_list.append({'field_name': 'dataset_publisher',
                                   'output_string': 'Publisher',
                                   'show_if_empty': True
                                   })
        specification_list.append({'field_name': 'dataset_release_date',
                                   'output_string': "Release date",
                                   'show_if_empty': True
                                   })
        specification_list.append({'field_name': 'other_citation_details',
                                   'output_string': "Other citation details",
                                   'show_if_empty': True
                                   })
        html = object_to_html(object, specification_list)
    else:
        print("Warning, calling str() to render an object")
        print("Object:", object)
        print("type(object):", type(object))
        html = str(object)

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