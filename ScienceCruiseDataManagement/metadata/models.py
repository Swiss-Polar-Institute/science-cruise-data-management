from django.db import models
from main.models import Person, Organisation, Platform
from main.models import Project as ExpeditionProject
from main.models import SpecificDevice as ExpeditionSpecificDevice
from data_storage_management.models import Item
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

############### DIF CONTROLLED VOCABULARY TABLES #################

class HorizontalResolutionRange(models.Model):
    horizontal_resolution_range	= models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date= models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.horizontal_resolution_range)


class Instrument(models.Model):
    category = models.CharField(max_length=255, null=True, blank=True)
    instrument_class = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=255, null=True, blank=True)
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {} - {} - {} - {} - {}".format(self.category, self.instrument_class, self.type, self.subtype, self.short_name, self.long_name)

    class Meta:
        unique_together = (('category','instrument_class','type', 'subtype', 'short_name', 'long_name'))


class Platform(models.Model):
    category = models.CharField(max_length=255, null=True, blank=True)
    series_entity = models.CharField(max_length=255, null=True, blank=True)
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)
    detailed_platform = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {} - {} - {} - {}".format(self.category, self.series_entity, self.short_name, self.long_name, self.detailed_platform)

    class Meta:
        unique_together = (('category', 'series_entity', 'short_name', 'long_name', 'detailed_platform', 'uuid'))


class Project(models.Model):
    bucket = models.CharField(max_length=255, null=True, blank=True)
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.short_name)

    class Meta:
        unique_together = (('bucket', 'short_name', 'long_name'))


class Provider(models.Model):
    bucket_Level0 = models.CharField(max_length=255, null=True, blank=True)
    bucket_Level1 = models.CharField(max_length=255, null=True, blank=True)
    bucket_Level2 = models.CharField(max_length=255, null=True, blank=True)
    bucket_Level3 = models.CharField(max_length=255, null=True, blank=True)
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)
    data_center_url = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {}".format(self.short_name, self.long_name)

    class Meta:
        unique_together = (('bucket_Level0', 'bucket_Level1', 'bucket_Level2', 'bucket_Level3', 'short_name', 'long_name'))


class RUContentType(models.Model):
    type = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.type)

    class Meta:
        unique_together = (('type', 'subtype'))


class TemporalResolutionRange(models.Model):
    temporal_resolution_range = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.temporal_resolution_range)


class VerticalResolutionRange(models.Model):
    vertical_resolution_range = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.vertical_resolution_range)


###### RECOMMENDED VOCABULARIES FOR THE DIF FIELDS #####
# Note that the tables that follow are not strictly controlled vocabularies but the possible choices are listed in the DIF Writer's Guide.

class DatasetRole(models.Model):
    role = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.role)


class DatasetProgress(models.Model):
    type = models.CharField(max_length=31, unique=True)
    description = models.CharField(max_length=255)
    download_date = models.DateTimeField()
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.type)

    class Meta:
        verbose_name_plural="Dataset progress"


class DistributionMedia(models.Model):
    media_type = models.CharField(max_length=80)
    distribution_media = models.CharField(max_length=80)
    download_date = models.DateTimeField()
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {}".format(self.media_type, self.distribution_media)

    class Meta:
        unique_together = (('media_type', 'distribution_media'))


class DistributionFormat(models.Model):
    distribution_format = models.CharField(max_length=80, null=True, blank=True)
    description = models.CharField(max_length=80)
    download_date = models.DateTimeField()
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {}".format(self.distribution_format, self.description)

    class Meta:
        unique_together = (('distribution_format', 'description'))


class IdnNode(models.Model):
    idn_node_short_name = models.CharField(max_length=255, null=True, blank=True)
    idn_node_use_description = models.CharField(max_length=255, null=True, blank=True)
    idn_node_long_name = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True,blank=True)
    revision_date = models.DateTimeField(null=True, blank=True)
    keyword_status = models.CharField(max_length=255, null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {} - {}".format(self.idn_node_short_name, self.idn_node_long_name, self.idn_node_use_description)

    class Meta:
        unique_together = (('idn_node_short_name', 'idn_node_use_description', 'idn_node_long_name'))


###### Datacite controlled vocabularies

# This table was included because the DIF personnel roles are very generic. If these metadata records are ever made into DOIs, then normally
# a more specific role (or in this case for the Datacite schema (v 3.1) contributor type) is required. This information was captured during
# the cruise to avoid having to contact PIs post cruise.

class DataciteContributorType(models.Model):
    contributor_type = models.CharField(max_length=50, unique=True)
    datacite_schema_version = models.CharField(max_length=10)
    in_datacite = models.BooleanField()

    def __str__(self):
        return "{}".format(self.contributor_type)


def data_set_citation_publisher_default():
    return text_to_ids([settings.METADATA_DEFAULT_CITATION_PUBLISHER], Provider, 'short_name')[0]

############## MAIN DIF METADATA MODELS ###############

class DataSetCitation(models.Model):
    dataset_creator = models.ManyToManyField(Person, blank=True)
    dataset_title = models.CharField(max_length=220, null=True, blank=True)
    dataset_release_date = models.DateField(null=True,blank=True)
    dataset_publisher = models.ForeignKey(Provider, default=data_set_citation_publisher_default, null=True, blank=True)
    version = models.CharField(max_length=10, default="1.0", null=True, blank=True)
    other_citation_details = models.CharField(max_length=255, null=True, blank=True,help_text='Additional free-text citation information. Put here about other grants and acknowledgements.')

    def __str__(self):
        return "{}".format(self.dataset_title)


class Personnel(models.Model):
    dataset_role = models.ManyToManyField('DatasetRole')
    datacite_contributor_type = models.ManyToManyField('DataciteContributorType')
    person = models.ForeignKey(Person, null=True, blank=True)

    def __str__(self):
        dataset_roles = self.dataset_role.all()
        dataset_role_str = ",".join([dataset_role.role for dataset_role in dataset_roles])
        datacite_contributor_types = self.datacite_contributor_type.all()
        datacite_contributor_type_str = ",".join([datacite_contributor_type.contributor_type for datacite_contributor_type in datacite_contributor_types ])
        return "{} - {} - {}".format(str(self.person), dataset_role_str, datacite_contributor_type_str)

    class Meta:
        verbose_name_plural = "Personnel"


class Parameter(models.Model):
    category = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    term = models.CharField(max_length=255)
    variable_level_1 = models.CharField(max_length=255, null=True, blank=True)
    variable_level_2 = models.CharField(max_length=255, null=True, blank=True)
    variable_level_3 = models.CharField(max_length=255, null=True, blank=True)
    detailed_variable = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {} - {} - {} - {} - {} - {}".format(self.category, self.topic, self.term, self.variable_level_1, self.variable_level_2, self.variable_level_3, self.detailed_variable)

    class Meta:
        unique_together = (('category', 'topic', 'term', 'variable_level_1', 'variable_level_2', 'variable_level_3', 'detailed_variable'))


class TemporalCoverage(models.Model):
    start_date = models.DateField(null=True, blank=True)
    stop_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.start_date, self.stop_date)


class SpatialCoverage(models.Model):
    southernmost_latitude = models.FloatField(null=True, blank=True, help_text='Decimal degrees. A minus sign, "-", placed immediately before the latitude value indicates a latitude south of the Equator (defined as 0 degrees latitude)')
    northernmost_latitude = models.FloatField(null=True, blank=True, help_text='Decimal degrees. A minus sign, "-", placed immediately before the latitude value indicates a latitude south of the Equator (defined as 0 degrees latitude)')
    westernmost_longitude = models.FloatField(null=True, blank=True, help_text='Decimal degrees. A minus sign, "-", placed immediately before the longitude value indicates a longitude west of the Prime Meridian (defined as 0 degrees).')
    easternmost_longitude = models.FloatField(null=True, blank=True, help_text='Decimal degrees. A minus sign, "-", placed immediately before the longitude value indicates a longitude west of the Prime Meridian (defined as 0 degrees).')
    minimum_altitude = models.FloatField(null=True, blank=True, help_text='Units must be specified.')
    maximum_altitude = models.FloatField(null=True, blank=True, help_text='Units must be specified.')
    minimum_depth = models.FloatField(null=True, blank=True, help_text='Units must be specified.')
    maximum_depth = models.FloatField(null=True, blank=True, help_text='Units must be specified.')

    def __str__(self):
        return "{} {} {} {}".format(self.southernmost_latitude, self.northernmost_latitude, self.westernmost_longitude, self.easternmost_longitude)


class Location(models.Model):
    location_category = models.CharField(max_length=255, null=True, blank=True)
    location_type = models.CharField(max_length=255, null=True, blank=True)
    location_subregion1 = models.CharField(max_length=255, null=True, blank=True)
    location_subregion2 = models.CharField(max_length=255, null=True, blank=True)
    location_subregion3 = models.CharField(max_length=255, null=True, blank=True)
    detailed_location = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {} - {} - {} - {} - {}".format(self.location_category, self.location_type, self.location_subregion1,
                                          self.location_subregion2, self.location_subregion3, self.detailed_location)

    class Meta:
        unique_together = (('location_category', 'location_type', 'location_subregion1', 'location_subregion2', 'location_subregion3', 'detailed_location'))


class DataResolution(models.Model):
    latitude_resolution = models.CharField(max_length=20, null=True, blank=True, help_text='The minimum difference between two adjacent latitude values.')
    longitude_resolution = models.CharField(max_length=20, null=True, blank=True, help_text='The minimum difference between two adjacent longitude values.')
    horizontal_resolution_range = models.ForeignKey('HorizontalResolutionRange', null=True, blank=True, help_text='The range should be selected based on the <Latitude_Resolution> and <Longitude_Resolution>.')
    vertical_resolution = models.CharField(max_length=20, null=True, blank=True, help_text='The minimum difference possible between two adjacent vertical values.')
    vertical_resolution_range = models.ForeignKey('VerticalResolutionRange', null=True, blank=True, help_text='The range should be selected based on the specified <Vertical_Resolution>.')
    temporal_resolution = models.CharField(max_length=20, null=True, blank=True, help_text='the frequency of data sampled.')
    temporal_resolution_range = models.ForeignKey('TemporalResolutionRange', null=True, blank=True, help_text='The range should be selected based on the specified <Temporal_Resolution>.')

    def __str__(self):
        return "{} {} {} {}".format(self.latitude_resolution, self.longitude_resolution, self.vertical_resolution, self.temporal_resolution)


class DataCenter(models.Model):
    data_center_name = models.ForeignKey('DataCenterName')
    data_set_id = models.CharField(max_length=80, null=True, blank=True, help_text="This is a data set identifier assigned by the data center (may or may not be the same as the <Entry_ID>.")
    personnel = models.ManyToManyField(Personnel, help_text="Contact information for the data.")

    def __str__(self):
        return "{} - {}".format(self.data_center_name, self.personnel)


class DataCenterName(models.Model):
    short_name = models.CharField(max_length=160)
    long_name = models.CharField(max_length=240, null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.short_name, self.long_name)


class Distribution(models.Model):
    distribution_media = models.ForeignKey('DistributionMedia', null=True, blank=True, help_text="The media options for the user receiving the data.")
    distribution_size = models.CharField(max_length=80, null=True, blank=True, help_text = "An approximate size (in KB, MB or GB) for the entire data set. Specify if data are compressed and the method of compression.")
    distribution_format = models.ManyToManyField('DistributionFormat', blank=True, help_text="The data format used to distribute the data.")
    fees = models.CharField(max_length=80, default="No cost", null=True, blank=True, help_text="Cost of <Distribution_Media> or distribution costs if any. Specify if there are no costs.")

    def __str__(self):
        formats = self.distribution_format.all()

        formats_str = ", ".join([str(format) for format in formats])

        return "{} - {} - {}".format(self.distribution_media, self.distribution_format, self.distribution_size)


class Summary(models.Model):
    abstract = models.TextField(help_text="Lineage statement.")
    purpose = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.abstract)

    class Meta:
        verbose_name_plural = "Summaries"


def text_to_ids(parameters, model, field):
    output = []

    for parameter in parameters:
        try:
            id = model.objects.get(**{field: parameter})
            output.append(getattr(id, "id"))

        except ObjectDoesNotExist:
            pass

    return output


def metadata_entry_platform_defaults():
    return text_to_ids(settings.METADATA_DEFAULT_PLATFORM_SHORT_NAME, Platform, 'short_name')


def metadata_entry_project_defaults():
    return text_to_ids(settings.METADATA_DEFAULT_PROJECT_SHORT_NAME, Project, 'short_name')


def metadata_entry_data_center_defaults():
    return text_to_ids(settings.METADATA_DEFAULT_DATA_CENTER, Provider, 'short_name')


def metadata_entry_idn_node_defaults():
    return text_to_ids(settings.METADATA_DEFAULT_IDN_NODE, IdnNode, 'idn_node_short_name')


##### Full metadata entry ######
class MetadataEntry(models.Model):
    entry_id = models.CharField(max_length=255, unique=True, help_text="Unique document identifier of the metadata record. The identifier is case insensitive. The <Entry_ID> consists of 1 to 80 alphanumeric characters of the UTF-8 set, including underbar (_), hyphen (-) and period (.).")
    entry_title = models.CharField(max_length=220, help_text="Title of the data set described by the metadata. For example, <Entry_Title>......collected in the Southern Ocean during the austral summer (January - February 2017) as part of the Antarctic Circumnavigation Experiment (ACE; leg 2 of 3). </Entry_Title> provides an adequate amount of information to guide the user.")
    data_set_citation = models.ForeignKey(DataSetCitation, null=True, blank=True)
    personnel = models.ManyToManyField(Personnel, help_text="The point of contact for more information about the data set or the metadata.")
    parameters = models.ManyToManyField(Parameter)
    sensor_name = models.ManyToManyField(Instrument, blank=True)
    expedition_specific_device = models.ManyToManyField(ExpeditionSpecificDevice, blank=True)
    source_name = models.ManyToManyField(Platform, blank=True, default=metadata_entry_platform_defaults)
    temporal_coverage = models.ManyToManyField(TemporalCoverage, blank=True)
    data_set_progress = models.ForeignKey(DatasetProgress, null=True, blank=True)
    spatial_coverage = models.ManyToManyField(SpatialCoverage, blank=True)
    location = models.ManyToManyField(Location, blank=True)
    data_resolution= models.ManyToManyField(DataResolution, blank=True)
    project = models.ManyToManyField(Project, blank=True, default=metadata_entry_project_defaults())
    quality = models.CharField(max_length=255, null=True, blank=True, help_text="This field allows the author to provide information about the quality of the data or any quality assurance procedures followed in producing the data. Include indicators of data quality or quality flags. Include recognized or potential problems with quality. Established quality control mechanisms should be included. Established quantitative quality measurements should be included.")
    access_constraints = models.TextField(null=True, blank=True, help_text="This field allows the author to provide information about any constraints for accessing the data set. This includes any special restrictions, legal prerequisites, limitations and/or warnings on obtaining the data set.")
    use_constraints = models.TextField(null=True, blank=True, help_text="This field allows the author to describe how the data may or may not be used after access is granted to assure the protection of privacy or intellectual property.  This includes any special restrictions, legal prerequisites, terms and conditions, and/or limitations on using the data set.  Data providers may request acknowledgement of the data from users and claim no responsibility for quality and completeness of data.")
    data_set_language = models.CharField(max_length=255, default=settings.DEFAULT_DATA_SET_LANGUAGE, null=True, blank=True, help_text="DEFAULT=English")
    originating_center = models.ForeignKey(Provider, related_name='originating_centre_provider', null=True, blank=True, help_text="The data center or data producer who originally generated the dataset.")
    data_center = models.ManyToManyField(Provider, default=metadata_entry_data_center_defaults, related_name='data_center_provider', help_text="The <Data Center> is the data center, organization, or institution responsible for distributing the data.")
    distribution = models.ManyToManyField(Distribution)
    summary = models.ForeignKey(Summary, help_text="This field provides a brief description of the data set along with the purpose of the data. This allows potential users to determine if the data set is useful for their needs.")
    parent_dif = models.CharField(max_length=255, null=True, blank=True)
    idn_node = models.ManyToManyField(IdnNode, default=metadata_entry_idn_node_defaults)
    metadata_name= models.CharField(max_length=255, default=settings.DEFAULT_METADATA_NAME, help_text="DEFAULT=CEOS IDN DIF")
    metadata_version = models.CharField(max_length=80, default=settings.DEFAULT_METADATA_VERSION, help_text="DEFAULT=VERSION 9.9")
    dif_creation_date = models.DateField(null=True, blank=True)
    last_dif_revision_date = models.DateField(null=True, blank=True)
    dif_revision_history = models.TextField(null=True, blank=True)
    future_dif_review_date = models.DateField(null=True, blank=True)
    private = models.BooleanField()
    expedition_project = models.ManyToManyField(ExpeditionProject)
    directory = models.ManyToManyField(Item, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.entry_id, self.entry_title)

    class Meta:
        verbose_name_plural = "Metadata entries"
