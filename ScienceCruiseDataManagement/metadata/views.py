from django.db import models
from django.shortcuts import render
import datetime
from main.models import Project
from metadata.models import *
from django.views.generic import TemplateView, ListView, View
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.template import loader
import types
from django.views.static import serve
import subprocess
from django.http import HttpResponse
import metadata.metadataentry_to_dif


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


def metadata_entry_context(id):
    try:
        metadata_entry = MetadataEntry.objects.get(id=id)
    except ObjectDoesNotExist:
        return "No metadata found"

    rows = []

    rows.append(('ID', render_object(metadata_entry.entry_id)))

    rows.append(('Title', render_object(metadata_entry.entry_title)))

    rows.append(('Data set citation', render_object(metadata_entry.data_set_citation, "<br>")))

    rows.append(('Personnel', render_object(metadata_entry.personnel.all().order_by('person__name_last'))))

    rows.append(('Parameters', render_object(metadata_entry.parameters.all().order_by('category', 'topic', 'term',
                                                                                      'variable_level_1', 'variable_level_2',
                                                                                      'variable_level_3', 'detailed_variable'))))

    rows.append(('Sensor names', render_object(metadata_entry.sensor_names())))

    rows.append(('Source names', render_object(metadata_entry.source_names())))

    rows.append(('Temporal coverage', render_object(metadata_entry.temporal_coverage)))

    rows.append(('Data set progress', render_object(metadata_entry.data_set_progress)))

    rows.append(('Spatial coverage', render_object(metadata_entry.spatial_coverage)))

    rows.append(('Location', render_object(metadata_entry.location.all().order_by('location_category',
                                                                                  'location_type',
                                                                                  'location_subregion1',
                                                                                  'location_subregion2',
                                                                                  'location_subregion3',
                                                                                  'detailed_location'))))

    rows.append(('Data resolution', "<ul><li>" + render_object(metadata_entry.data_resolution, separator="<li>") + "</ul>"))

    rows.append(('Projects', render_object(metadata_entry.project)))

    rows.append(('Quality', render_object(metadata_entry.quality, "<br>")))

    rows.append(('Access constraints', render_object(metadata_entry.access_constraints)))

    rows.append(('Use constraints', render_object(metadata_entry.use_constraints)))

    rows.append(('Data set language', render_object(metadata_entry.data_set_language)))

    rows.append(('Originating center', render_object(metadata_entry.originating_center)))

    rows.append(('Data center', render_object(metadata_entry.data_centers)))

    # rows.append(('Distribution', render_object(metadata_entry.distribution.all())))
    rows.append(('Distribution', render_object(Distribution.objects.filter(metadata_entry=id))))

    rows.append(('Summary', render_object(metadata_entry.summary)))

    rows.append(('Parent DIF', render_object(metadata_entry.parent_difs)))

    rows.append(('IDN node', render_object(metadata_entry.idn_node)))

    rows.append(('Metadata name', render_object(metadata_entry.metadata_name)))

    rows.append(('Metadata version', render_object(metadata_entry.metadata_version)))

    rows.append(('DIF creation date', render_object(metadata_entry.dif_creation_date)))

    rows.append(('Last DIF revision date', render_object(metadata_entry.last_dif_revision_date)))

    rows.append(('DIF revision history', render_object(metadata_entry.dif_revision_history)))

    rows.append(('Future DIF review date', render_object(metadata_entry.future_dif_review_date)))

    rows.append(('Private', render_object(metadata_entry.private)))

    rows.append(('Directories', render_object(metadata_entry.directories())))

    context = {}
    context['rows'] = rows
    context['metadata_entry_id'] = id
    return context


class MetadataEntryAsDif(TemplateView):
    def get(self, request, *args, **kwargs):
        id = args[0]

        metadata_entry = MetadataEntry.objects.get(id=id)
        record_generator = metadata.metadataentry_to_dif.MetadataRecordGenerator(metadata_entry)
        result = record_generator.do()

        (ok, messages) = metadata.metadataentry_to_dif.validate(result)

        if ok:
            response = HttpResponse(result, content_type="application/xml")

            filename = "metadata-record-{}.xml".format(metadata_entry.entry_id)
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

            return response
        else:
            messages = "ERROR VALIDATING DIF. Output of xmllint:\n" + messages.decode('utf-8')
            response = HttpResponse(messages, content_type="text/plain")

            return response

    # s._headers['content-disposition'] = (('Content-Disposition', 'attachment; filename="{}"'.format(filename)))


class MetadataEntryAsWord(TemplateView):
    def get(self, request, *args, **kwargs):
        id = args[0]
        context = metadata_entry_context(id)
        context['exporting'] = True
        content = loader.render_to_string("metadata_entry.html",
                                          context, request)

        f = open("/tmp/content.html", "w")
        f.write(content)
        f.close()

        s = subprocess.Popen(["pandoc", "-o", "/tmp/content.docx", "/tmp/content.html"])
        s.wait()

        metadata_entry = MetadataEntry.objects.get(id=id)

        filename = "metadata-{}.docx".format(metadata_entry.entry_id)

        s = serve(request, "content.docx", "/tmp")
        s._headers['content-disposition'] = (('Content-Disposition', 'attachment; filename="{}"'.format(filename)))
        return s

class MetadataEntryView(TemplateView):
    template_name = "metadata_entry.html"

    def get(self, request, *args, **kwargs):
        id = int(args[0])

        return render(request, "metadata_entry.html", metadata_entry_context(id))

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


def object_to_html(object, specification_list, separator):
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

        output += line_output + render_object(output_text) + separator

    return output

def render_iterable(qs, separator):
    output = set()

    for object in qs:
        output.add(render_object(object))

    return separator.join(sorted(output))


def render_object(object, separator="<br>"):
    is_many_to_many = True
    try:
        object.all()
    except AttributeError:
        is_many_to_many = False

    if isinstance(object, Person):
        html = "{} {}".format(object.name_first, object.name_last)
    elif isinstance(object, models.QuerySet) or isinstance(object, list):
        html = render_iterable(object, separator)
    elif is_many_to_many:
        objects = object.all()
        html = render_object(objects, separator=separator)
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

        html = object_to_html(object, specification_list, separator)
    elif isinstance(object, DistributionMedia):
        html = object.media_type
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

        html = object_to_html(object, specification_list, separator)
    elif isinstance(object, DeviceType):
        html = object.name
    elif isinstance(object, Item):
        html = object.destination_directory
    elif object is None:
        html = "-"
    else:
        print("Warning, calling str() to render an object. Type:",type(object),"object:",object)
        html = str(object).replace("\n", separator)

    return html