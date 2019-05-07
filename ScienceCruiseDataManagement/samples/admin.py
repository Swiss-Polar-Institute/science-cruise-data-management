from django.forms import ModelForm
from django.contrib import admin

import samples.models
import main.models

#
# class SampleForm(ModelForm):
#     class Meta:
#         model = samples.models.Sample
#         fields = '__all__'


class SampleAdmin(main.admin.ReadOnlyIfUserCantChange, main.admin.import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_type', 'storage_location', 'offloading_port', 'destination', 'ship', 'mission', 'leg', 'project', 'julian_day', 'event', 'pi', 'preservation', 'file', 'specific_contents')
    fields = list_display
    ordering = ['expedition_sample_code']
    readonly_fields = ('expedition_sample_code', )
    list_filter = (main.admin_filters.ProjectFilter, main.admin_filters.LegFilter, main.admin_filters.SampleContentsFilter, main.admin_filters.TypeOfStorageFilter, main.admin_filters.StorageLocationFilter, main.admin_filters.OffloadingPortFilter, main.admin_filters.EventFilter)
    search_fields = ('expedition_sample_code', 'project_sample_number', 'contents', 'crate_number', 'storage_location', 'offloading_port', 'destination', 'julian_day', 'event__number', 'pi_initials__initials', 'preservation__name', 'file', 'specific_contents')
    # form = SampleForm


class StorageTypeAdmin(main.admin.import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'created_on_date_time', 'created_by')
    exclude = ('created_by',)
    ordering = ['name']


admin.site.register(samples.models.StorageType, StorageTypeAdmin)
admin.site.register(samples.models.Sample, SampleAdmin)
