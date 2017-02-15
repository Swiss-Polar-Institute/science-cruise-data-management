from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField
import metadata.models

from metadata.admin_filters import ParameterFilter

class TextWithId(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{}-{}".format(obj.id, str(obj))


class MetadataEntryForm(ModelForm):
    parameters = TextWithId(queryset=metadata.models.Parameter.objects.all())
    sensor_name = TextWithId(queryset=metadata.models.Instrument.objects.all())
    source_name = TextWithId(queryset=metadata.models.Platform.objects.all())
    location = TextWithId(queryset=metadata.models.Location.objects.all())
    originating_data_center = TextWithId(queryset=metadata.models.Provider.objects.all())

    class Meta:
        model = metadata.models.MetadataEntry
        fields = '__all__'


class MetadataEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_id', 'entry_title', 'data_set_citation_list', 'personnel_list', 'parameters_list', 'sensor_name_list',
                    'expedition_specific_device_list', 'source_name_list', 'temporal_coverage_list', 'data_set_progress', 'spatial_coverage_list', 'location_list',
                    'data_resolution_list', 'project_list', 'quality', 'access_constraints', 'use_constraints',
                    'data_set_language', 'originating_center', 'data_center_list', 'distribution_list', 'summary',
                    'parent_dif', 'idn_node_list', 'metadata_name', 'metadata_version', 'dif_creation_date',
                    'last_dif_revision_date', 'dif_revision_history', 'future_dif_review_date', 'private')
    ordering = ['entry_id']
    filter_horizontal = ('parameters',)

    form = MetadataEntryForm

    def data_set_citation_list(self, obj):
        citations = obj.data_set_citation.all()

        return ",".join([str(citation) for citation in citations])

    def personnel_list(self, obj):
        people = obj.project.all()

        return ",".join([str(person) for person in people])

    def parameters_list(self, obj):
        parameters = obj.parameters.all()

        return ",".join([str(parameter) for parameter in parameters])

    def sensor_name_list(self, obj):
        sensor_names = obj.sensor_name.all()

        return ",".join([str(sensor_name) for sensor_name in sensor_names])

    def expedition_specific_device_list(self, obj):
        expedition_specific_devices = obj.expedition_specific_device.all()

        return ",".join([str(expedition_specific_devices) for expedition_specific_device in expedition_specific_devices])

    def source_name_list(self, obj):
        source_names = obj.source_name.all()

        return ",".join([str(source_name) for source_name in source_names])

    def temporal_coverage_list(self, obj):
         temporal_coverages = obj.temporal_coverage.all()

         return ",".join([str(temporal_coverage) for temporal_coverage in temporal_coverages])

    def spatial_coverage_list(self, obj):
        spatial_coverages = obj.spatial_coverage.all()

        return ",".join([str(spatial_coverage) for spatial_coverage in spatial_coverages])

    def location_list(self, obj):
        locations = obj.location.all()

        return ",".join([str(location) for location in locations])

    def data_resolution_list(self, obj):
        data_resolutions = obj.data_resolution.all()

        return ",".join([str(data_resolution) for data_resolution in data_resolutions])

    def project_list(self, obj):
        projects = obj.project.all()

        return ",".join([str(project) for project in projects])

    def data_center_list(self, obj):
        data_centers = obj.data_center.all()

        return ",".join([str(data_center) for data_center in data_centers])

    def distribution_list(self, obj):
        distributions = obj.distribution.all()

        return ",".join([str(distribution) for distribution in distributions])

    def idn_node_list(self, obj):
        idn_nodes = obj.idn_node.all()

        return ",".join([str(idn_node) for idn_node in idn_nodes])


class DataSetCitationAdmin(admin.ModelAdmin):
    list_display = ('dataset_creator', 'dataset_title', 'dataset_release_date', 'dataset_publisher',
                    'version', 'other_citation_details')


class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('dataset_role_list', 'datacite_contributor_type_list',
                    'person', 'email', 'contact_address')
    search_fields =('dataset_role_list', 'person')

    def dataset_role_list(self, obj):
        dataset_roles = obj.dataset_role.all()

        return ",".join([str(dataset_role) for dataset_role in dataset_roles])

    def datacite_contributor_type_list(self, obj):
        datacite_contributor_types = obj.datacite_contributor_type.all()

        return ",".join([str(datacite_contributor_type) for datacite_contributor_type in datacite_contributor_types])


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('category', 'topic', 'term', 'variable_level_1', 'variable_level_2',
                    'variable_level_3', 'detailed_variable', 'uuid', 'download_date',
                    'keyword_version', 'keyword_revision_date', 'in_gcmd')
    search_fields = ('category', 'topic', 'term', 'variable_level_1', 'variable_level_2',
                    'variable_level_3', 'detailed_variable')
    list_filter = (ParameterFilter,)


class TemporalCoverageAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'stop_date')


class SpatialCoverageAdmin(admin.ModelAdmin):
    list_display = ('southernmost_latitude', 'northernmost_latitude', 'westernmost_longitude', 'easternmost_longitude',
                    'minimum_altitude', 'maximum_altitude', 'minimum_depth', 'maximum_depth')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_category', 'location_type', 'location_subregion1',
                    'location_subregion2', 'location_subregion3', 'detailed_location', 'uuid',
                    'keyword_version', 'keyword_revision_date', 'download_date', 'in_gcmd')
    search_fields = ('location_category', 'location_type', 'location_subregion1',
                    'location_subregion2', 'location_subregion3', 'detailed_location')


class DataResolutionAdmin(admin.ModelAdmin):
    list_display = ('latitude_resolution', 'longitude_resolution', 'horizontal_resolution_range',
                    'vertical_resolution', 'vertical_resolution_range', 'temporal_resolution',
                    'temporal_resolution_range')


class DataCenterAdmin(admin.ModelAdmin):
    list_display = ('data_center_name', 'data_set_id', 'personnel_list')
    search_fields = ('data_center_name',)

    def personnel_list(self, obj):
        people = obj.project.all()

        return ",".join([str(person) for person in people])


class DataCenterNameAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name')


class DistributionAdmin(admin.ModelAdmin):
    list_display = ('distribution_media', 'distribution_size', 'distribution_format', 'fees')


class SummaryAdmin(admin.ModelAdmin):
    list_display = ('abstract', 'purpose')


class IdnNodeAdmin(admin.ModelAdmin):
    list_display = ('idn_node_short_name', 'idn_node_use_description', 'idn_node_long_name', 'keyword_version', 'revision_date',
                    'keyword_status', 'download_date')
    search_fields = ('idn_node_short_name', 'idn_node_use_description', 'idn_node_long_name')


class HorizontalResolutionRangeAdmin(admin.ModelAdmin):
    list_display = ('horizontal_resolution_range', 'uuid', 'keyword_version', 'keyword_revision_date', 'download_date', 'in_gcmd')
    search_fields = ('horizontal_resolution_range',)


class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('category', 'instrument_class', 'type', 'subtype', 'short_name', 'long_name',
                    'uuid', 'keyword_version', 'keyword_revision_date', 'download_date', 'in_gcmd')
    search_fields = ('category', 'instrument_class', 'type', 'subtype', 'short_name', 'long_name')


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('category', 'series_entity', 'short_name', 'long_name', 'detailed_platform', 'uuid', 'keyword_version',
                    'keyword_revision_date', 'download_date', 'in_gcmd')
    search_fields = ('category', 'series_entity', 'short_name', 'long_name', 'detailed_platform')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('bucket', 'short_name', 'long_name', 'uuid', 'keyword_version',
                    'keyword_revision_date', 'download_date', 'in_gcmd')
    search_fields = ('bucket', 'short_name', 'long_name')


class ProviderAdmin(admin.ModelAdmin):
    list_display = ('bucket_Level0', 'bucket_Level1', 'bucket_Level2', 'bucket_Level3',
                    'short_name', 'long_name', 'data_center_url', 'uuid', 'keyword_version',
                    'keyword_revision_date', 'download_date', 'in_gcmd')
    search_fields = ('bucket_Level0', 'bucket_Level1', 'bucket_Level2', 'bucket_Level3',
                    'short_name', 'long_name', 'data_center_url')


class RUContentTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'subtype', 'uuid', 'keyword_version', 'keyword_revision_date',
                    'download_date', 'in_gcmd')
    search_fields = ('type', 'subtype')


class TemporalResolutionRangeAdmin(admin.ModelAdmin):
    list_display = ('temporal_resolution_range', 'uuid', 'keyword_version', 'keyword_revision_date',
                    'download_date', 'in_gcmd')
    search_fields = ('temporal_resolution_range',)


class VerticalResolutionRangeAdmin(admin.ModelAdmin):
    list_display = ('vertical_resolution_range', 'uuid', 'keyword_version', 'keyword_revision_date',
                    'download_date', 'in_gcmd')
    search_fields = ('vertical_resolution_range',)


class DatasetRoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'description', 'in_gcmd')
    search_fields = ('role',)


class DatasetProgressAdmin(admin.ModelAdmin):
    list_display = ('type', 'description', 'download_date', 'in_gcmd')
    search_fields = ('type', 'description')


class DistributionMediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'distribution_media', 'download_date', 'in_gcmd')
    search_fields = ('media_type', 'distribution_media')


class DistributionFormatAdmin(admin.ModelAdmin):
    list_display = ('distribution_format', 'description', 'download_date', 'in_gcmd')
    search_fields = ('distribution_format', 'description')


class DataciteContributorTypeAdmin(admin.ModelAdmin):
    list_display = ('contributor_type', 'datacite_schema_version', 'in_datacite')
    search_fields = ('contributor_type',)


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
admin.site.register(metadata.models.TemporalResolutionRange, TemporalResolutionRangeAdmin)
admin.site.register(metadata.models.Project, ProjectAdmin)
admin.site.register(metadata.models.DistributionMedia, DistributionMediaAdmin)
admin.site.register(metadata.models.DataCenterName, DataCenterNameAdmin)
