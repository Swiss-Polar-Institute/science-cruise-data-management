from django.shortcuts import render
from main.models import Project
from metadata.models import MetadataEntry
from django.views.generic import TemplateView, ListView


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