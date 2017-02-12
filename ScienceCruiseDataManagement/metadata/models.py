from django.db import models
from main.models import Person, Organisation, Platform

############## MAIN DIF METADATA MODELS ###############

class MetadataEntry(models.Model):
    entry_id = models.CharField(max_length=255, unique=True, help_text="Unique document identifier of the metadata record. The identifier is case insensitive. The <Entry_ID> consists of 1 to 80 alphanumeric characters of the UTF-8 set, including underbar (_), hyphen (-) and period (.).")
    entry_title= models.CharField(max_length=220, help_text="Title of the data set described by the metadata. For example, <Entry_Title>Aerosol characterization and snow chemistry at Terra Nova Bay 2001-2003 </Entry_Title> provides an adequate amount of information to guide the user.")
    data_set_citation = models.ManyToManyField(DataSetCitation, null=True, blank=True)
    personnel = models.ManyToManyField(Personnel, help_text="The point of contact for more information about the data set or the metadata.")
    parameters = models.ManyToManyField(Parameter)
    sensor_name = models.ManyToManyField(Instrument, null=True, blank=True)
    source_name = models.ManyToManyField(Platform, null=True, blank=True)
    temporal_coverage = models.ManyToManyField(TemporalCoverage, null=True, blank=True)
    data_set_progress = models.ForeignKey(DatasetProgress, null=True, blank=True)
    spatial_coverage = models.ManyToManyField(SpatialCoverage,null=True,blank=True)
    location = models.ManyToManyField(Location, null=True, blank=True)
    data_resolution= models.ManyToManyField(DataResolution, null=True, blank=True)
    project = models.ManyToManyField(Project, null=True, blank=True)
    quality = models.CharField(max_length=255, null=True, blank=True, help_text="This field allows the author to provide information about the quality of the data or any quality assurance procedures followed in producing the data. Include indicators of data quality or quality flags. Include recognized or potential problems with quality. Established quality control mechanisms should be included. Established quantitative quality measurements should be included.")
    access_constraints = models.TextField(null=True, blank=True, help_text="This field allows the author to provide information about any constraints for accessing the data set. This includes any special restrictions, legal prerequisites, limitations and/or warnings on obtaining the data set.")
    use_constraints = models.TextField(null=True, blank=True, help_text="This field allows the author to describe how the data may or may not be used after access is granted to assure the protection of privacy or intellectual property.  This includes any special restrictions, legal prerequisites, terms and conditions, and/or limitations on using the data set.  Data providers may request acknowledgement of the data from users and claim no responsibility for quality and completeness of data.")
    data_set_language = models.CharField(max_length=255, null=True, blank=True, help_text="DEFAULT=English")
    originating_center = models.CharField(max_length=240, null=True, blank=True, help_text="The data center or data producer who originally generated the dataset.")
    data_center = models.ManyToManyField(Provider, help_text="The <Data Center> is the data center, organization, or institution responsible for distributing the data.")
    distribution = models.ManyToManyField(Distribution, null=True, blank=True)
    summary = models.ForeignKey(Summary, help_text="This field provides a brief description of the data set along with the purpose of the data. This allows potential users to determine if the data set is useful for their needs.")
    parent_dif = models.CharField(max_length=255, null=True, blank=True)
    idn_node = models.ManyToManyField(IdnNode, null=True, blank=True)
    metadata_name= models.CharField(max_length=255, help_text="DEFAULT=CEOS IDN DIF")
    metadata_version = models.CharField(max_length=80, help_text="DEFAULT=VERSION 9.9")
    dif_creation_date = models.CharField(max_length=50, null=True, blank=True)
    last_dif_revision_date = models.CharField(max_length=50, null=True, blank=True)
    dif_revision_history = models.TextField(null=True, blank=True)
    future_dif_review_date = models.CharField(null=True, blank=True)
    private = models.CharField(max_length=10, null=True, blank=True, help_text="True or False")

    def __str__(self):
        return "{}-{}".format(self.entry_id, self.entry_title)


class DataSetCitation(models.Model):
    dataset_creator = models.ForeignKey(Person, null=True, blank=True)
    dataset_title = models.CharField(max_length=255, null=True, blank=True)
    dataset_release_date = models.DateField(null=True,blank=True)
    dataset_publisher = models.ForeignKey(Organisation, null=True, blank=True)
    version = models.CharField(max_length=10, null=True, blank=True)
    other_citation_details = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.dataset_title)


class Personnel(models.Model):
    dataset_role = models.ManyToManyField(DatasetRole)
    datacite_contributor_type = models.ManyToManyField(DataciteContributorType)
    first_name = models.OneToOneField(Person, null=True, blank=True)
    last_name = models.OneToOneField(Person)
    email= models.CharField(max_length=80, null=True, blank=True)
    contact_address = models.ForeignKey(Organisation, null=True, blank=True)

    def __str__(self):
        return "{} {} - {}".format(self.first_name, self.last_name, self.role)


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
        return "{} - {} - {}".format(self.category, self.topic, self.term)


class TemporalCoverage(models.Model):
    start_date = models.DateField(null=True, blank=True)
    stop_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.start_date, self.stop_date)


class SpatialCoverage(models.Model):
    southernmost_latitude = models.CharField(max_length=10, null=True, blank=True)
    northernmost_latitude = models.CharField(max_length=10, null=True, blank=True)
    westernmost_longitude = models.CharField(max_length=10, null=True, blank=True)
    easternmost_longitude = models.CharField(max_length=10, null=True, blank=True)
    minimum_altitude = models.CharField(max_length=10, null=True, blank=True)
    maximum_altitude = models.CharField(max_length=10, null=True, blank=True)
    minimum_depth = models.CharField(max_length=10, null=True, blank=True)
    maximum_depth = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return "{} {} {} {}".format(self.southernmost_latitude, self.northernmost_latitude, self.westernmost_longitude, self.easternmost_longitude)


class Location(models.Model):
    location_category = models.CharField(max_length=255, null=True, blank=True)
    location_type = models.CharField(max_length=255, null=True, blank=True)
    location_subregion1 = models.CharField(max_length=255, null=True, blank=True)
    location_subregion2 = models.CharField(max_length=255, null=True, blank=True)
    location_subregion3 = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{} - {} - {} - {}".format(self.Location_Category, self.Location_Type, self.Location_Subregion1,
                                          self.Location_Subregion2)


class DataResolution(models.Model):
    latitude_resolution = models.CharField(max_length=20, null=True, blank=True)
    longitude_resolution = models.CharField(max_length=20, null=True, blank=True)
    horizontal_resolution_range = models.ForeignKey(HorizontalResolutionRange, null=True, blank=True)
    vertical_resolution = models.CharField(max_length=20, null=True, blank=True)
    vertical_resolution_range = models.ForeignKey(VerticalResolutionRange, null=True, blank=True)
    temporal_resolution = models.CharField(max_length=20, null=True, blank=True)
    temporal_resolution_range = models.ForeignKey(TemporalResolutionRange, null=True, blank=True)

    def __str__(self):
        return "{} {} {} {}".format(self.latitude_resolution, self.longitude_resolution, self.vertical_resolution, self.temporal_resolution)


class DataCenter(models.Model):
    data_center_name = models.ForeignKey(DataCenterName)
    data_set_id = models.CharField(max_length=255, null=True, blank=True, help_text="is a data set identifier assigned by the data center (may or may not be the same as the <Entry_ID>.")
    personnel = models.ManyToManyField(Personnel, help_text="Contact information for the data.")

    def __str__(self):
        return "{}".format(self.data_center_name)


class DataCenterName(models.Model):
    short_name = models.CharField(max_length=160)
    long_name = models.CharField(max_length=240, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.short_name)


class Distribution(models.Model):
    distribution_media = models.ForeignKey(DistributionMedia, null=True, blank=True, help_text="The media options for the user receiving the data.")
    distribution_size = models.CharField(max_length=80, null=True, blank=True, help_text = "An approximate size (in KB, MB or GB) for the entire data set. Specify if data are compressed and the method of compression.")
    distribution_format = models.ForeignKey(DistributionFormat, null=True, blank=True, help_text="The data format used to distribute the data.")
    fees = models.CharField(max_length=80, null=True, blank=True, help_text="Cost of <Distribution_Media> or distribution costs if any. Specify if there are no costs.")

    def __str__(self):
        return "{} {} {}".format(self.distribution_media, self.distribution_format, self.distribution_size)


class Summary(models.Model):
    abstract = models.TextField()
    purpose = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.abstract)


class IdnNode(models.Model):
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.TextField(null=True, blank=True)


############### DIF CONTROLLED VOCABULARY TABLES #################

class HorizontalResolutionRange(models.Model):
    horizontal_resolution_range	= models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date= models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.Horizontal_Resolution_Range)


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
        return "{}".format(self.Short_Name)


class Platform(models.Model):
    category = models.CharField(max_length=255, null=True, blank=True)
    series_entity = models.CharField(max_length=255, null=True, blank=True)
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.Short_Name)


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
        return "{}".format(self.Short_Name)


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
        return "{}".format(self.Short_Name)


class RUContentType(models.Model):
    type = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.Type)


class TemporalResolutionRange(models.Model):
    temporal_resolution_range = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.Temporal_Resolution_Range)


class VerticalResolutionRange(models.Model):
    vertical_resolution_range = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.Vertical_Resolution_Range)


###### RECOMMENDED VOCABULARIES FOR THE DIF FIELDS #####
# Note that the tables that follow are not strictly controlled vocabularies but the possible choices are listed in the DIF Writer's Guide.

class DatasetRole(models.Model):
    role = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.role)


class DatasetProgress(models.Model):
    type = models.CharField(max_length=31, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    download_date = models.DateTimeField()
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.type)


class DistributionMedia(models.Model):
    media_type = models.CharField(max_length=80)
    distribution_media = models.CharField(max_length=80)
    download_date = models.DateTimeField()
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.distribution_media)


class DistributionFormat(models.Model):
    distribution_format = models.CharField(max_length=80)
    description = models.CharField(max_length=80, null=True, blank=True)
    download_date = models.DateTimeField()
    in_gcmd = models.BooleanField()

    def __str__(self):
        return "{}".format(self.distribution_format)

###### Datacite controlled vocabularies

# This table was included because the DIF personnel roles are very generic. If these metadata records are ever made into DOIs, then normally
# a more specific role (or in this case for the Datacite schema (v 3.1) contributor type) is required. This information was captured during
# the cruise to avoid having to contact PIs post cruise.

class DataciteContributorType(models.Model):
    contributor_seq = models.IntegerField()
    contributor_type = models.CharField(max_length=50)
    version = models.CharField(max_length=10)
    in_datacite = models.BooleanField()

    def __str__(self):
        return "{}".format(self.contributor_type)








