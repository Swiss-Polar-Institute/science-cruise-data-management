from django.contrib import admin
import metadata.models


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


class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('dataset_role', 'datacite_contributor_type', 'first_name', 'last_name', 'email', 'contact_address')


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('category', 'topic', 'term', 'variable_level_1', 'variable_level_2',
                    'variable_level_3', 'detailed_variable', 'uuid', 'download_date',
                    'keyword_version', 'keyword_revision_date', 'in_gcmd')


class TemporalCoverageAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'stop_date')


class SpatialCoverageAdmin(admin.ModelAdmin):
    list_display = ('southernmost_latitude', 'northernmost_latitude', 'westernmost_longitude', 'easternmost_longitude',
                    'minimum_altitude', 'maximum_altitude', 'minimum_depth', 'maximum_depth')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_category', 'location_type', 'location_subregion1',
                    'location_subregion2', 'location_subregion3', 'uuid',
                    'keyword_version', 'keyword_revision_date', 'download_date', 'in_gcmd')


class DataResolutionAdmin(admin.ModelAdmin):
    list_display = ('latitude_resolution', 'longitude_resolution', 'horizontal_resolution_range',
                    'vertical_resolution', 'vertical_resolution_range', 'temporal_resolution',
                    'temporal_resolution_range')


class DataCenterAdmin(admin.ModelAdmin):
    list_display = ('data_center_name', 'data_set_id', 'personnel')


class DistributionAdmin(admin.ModelAdmin):
    list_display = ('distribution_media', 'distribution_size', 'distribution_format', 'fees')


class SummaryAdmin(admin.ModelAdmin):
    list_display = ('abstract', 'purpose')


class IdnNodeAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name')


class HorizontalResolutionRangeAdmin(admin.ModelAdmin):
    list_display = ('horizontal_resolution_range', 'uuid', 'keyword_version', 'keyword_revision_date', 'download_date', 'in_gcmd')


class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('category', 'instrument_class', 'type', 'subtype', 'short_name', 'long_name',
                    'uuid', 'keyword_version', 'keyword_revision_date', 'download_date', 'in_gcmd')


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('category', 'series_entity', 'short_name', 'long_name', 'uuid', 'keyword_version',
                    'keyword_revision_date', 'download_date', 'in_gcmd')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('bucket', 'short_name', 'long_name', 'uuid', 'keyword_version',
                    'keyword_revision_date', 'download_date', 'in_gcmd')


class ProviderAdmin(admin.ModelAdmin):
    list_display = ('bucket_Level0', 'bucket_Level1', 'bucket_Level2', 'bucket_Level3',
                    'short_name', 'long_name', 'data_center_url', 'uuid', 'keyword_version',
                    'keyword_revision_date', 'download_date', 'in_gcmd')


class RUContentTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'subtype', 'uuid', 'keyword_version', 'keyword_revision_date',
                    'download_date', 'in_gcmd')


class TemporalResolutionRangeAdmin(admin.ModelAdmin):
    list_display = ('temporal_resolution_range', 'uuid', 'keyword_version', 'keyword_revision_date',
                    'download_date', 'in_gcmd')


class VerticalResolutionRangeAdmin(admin.ModelAdmin):
    list_display = ('vertical_resolution_range', 'uuid', 'keyword_version', 'keyword_revision_date',
                    'download_date', 'in_gcmd')


class DatasetRoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'description', 'in_gcmd')


class DatasetProgressAdmin(admin.ModelAdmin):
    list_display = ('type', 'description', 'download_date', 'in_gcmd')


class DistributionMediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'distribution_media', 'download_date', 'in_gcmd')


class DistributionFormatAdmin(admin.ModelAdmin):
    list_display = ('distribution_media', 'distribution_size', 'distribution_format', 'fees')


class DataciteContributorTypeAdmin(admin.ModelAdmin):
    list_display = ('contributor_type', 'datacite_schema_version', 'in_datacite')


admin.site.register(metadata.models.MetadataEntry, MetadataEntryAdmin)
admin.site.register(metadata.models.DataSetCitation, DataSetCitationAdmin)
admin.site.register(metadata.models.Personnel, PersonnelAdmin)
admin.site.register(metadata.models.Parameter, ParameterAdmin)
admin.site.register(metadata.models.TemporalCoverage, TemporalCoverageAdmin)
admin.site.register(metadata.models.SpatialCoverage, SpatialCoverageAdmin)
admin.site.register(metadata.models.Location, LocationAdmin)
admin.site.register(metadata.models.DataResolution, DataResolutionAdmin)
admin.site.register(metadata.models.DataCenter, DataCenterAdmin)
admin.site.register(metadata.models.Distribution, DistributionAdmin)
admin.site.register(metadata.models.Summary, SummaryAdmin)
admin.site.register(metadata.models.IdnNode, IdnNodeAdmin)
admin.site.register(metadata.models.HorizontalResolutionRange, HorizontalResolutionRangeAdmin)
admin.site.register(metadata.models.Instrument, InstrumentAdmin)
admin.site.register(metadata.models.Platform, PlatformAdmin)
admin.site.register(metadata.models.Provider, ProviderAdmin)
admin.site.register(metadata.models.RUContentType, RUContentTypeAdmin)
admin.site.register(metadata.models.VerticalResolutionRange, VerticalResolutionRangeAdmin)
admin.site.register(metadata.models.DatasetRole, DatasetRoleAdmin)
admin.site.register(metadata.models.DatasetProgress, DatasetProgressAdmin)
admin.site.register(metadata.models.DistributionFormat, DistributionFormatAdmin)
admin.site.register(metadata.models.DataciteContributorType, DataciteContributorTypeAdmin)