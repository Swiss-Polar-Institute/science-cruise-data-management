from django.contrib import admin

class MetadataEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_id', 'entry_title', 'data_set_citation', 'personnel', 'parameters', 'sensor_name',
                    'source_name', 'temporal_coverage', 'data_set_progress', 'spatial_coverage', 'location',
                    'data_resolution', 'project', 'quality', 'access_constraints', 'use_constraints',
                    'data_set_language', 'originating_center', 'data_center', 'distribution', 'summary',
                    'parent_dif', 'idn_node', 'metadata_name', 'metadata_version', 'dif_creation_date',
                    'last_dif_revision_date', 'dif_revision_history', 'future_dif_review_date', 'private')
    ordering = ['entry_id']

class DataSetCitationAdmin(admin.ModelAdmin):
    list_display = ('dataset_creator', 'dataset_title', 'dataset_release_date', 'dataset_publisher',
                    'version', 'other_citation_details')
    ordering = ['dataset_creator']

# class
