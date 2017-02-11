from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from smart_selects.db_fields import ChainedManyToManyField
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from main.models import Person, Organisation, SpecificDevice, Platform, Mission

############## MAIN DIF METADATA MODELS ###############

class MetadataEntry(models.Model):
    entry_id = models.CharField(max_length=255, unique=True)
    entry_title= models.CharField(max_length=255)
    data_set_citation = models.ManyToManyField(DataSetCitation, null=True, blank=True)
    personnel = models.ManyToManyField(Person)
    parameters = models.ManyToManyField(Parameter)
    iso_topic_category = models.ManyToManyField(IsoTopicCategory)
    sensor_name = models.ManyToManyField(SpecificDevice, null=True, blank=True)
    source_name = models.ManyToManyField(Platform, null=True, blank=True)
    temporal_coverage = models.ManyToManyField(TemporalCoverage, null=True, blank=True)
    data_set_progress = models.CharField(max_length=255, null=True, blank=True)
    spatial_coverage = models.ManyToManyField(SpatialCoverage,null=True,blank=True)
    location = models.ManyToManyField(Location, null=True, blank=True)
    data_resolution= models.ManyToManyField(DataResolution, null=True, blank=True)
    project = models.ManyToManyField(Mission, null=True, blank=True)
    quality = models.CharField(max_length=255, null=True, blank=True)
    access_constraints = models.CharField(max_length=255, null=True, blank=True)
    use_constraints = models.CharField(max_length=255, null=True, blank=True)
    data_set_language = models.CharField(max_length=255, null=True, blank=True)
    originating_centre = models.CharField(max_length=255, null=True, blank=True)
    data_centre = models.ManyToManyField(Organisation)
    distribution = models.ManyToManyField(Distribution, null=True, blank=True)
    summary = models.ForeignKey(Summary)
    parent_dif = models.CharField(max_length=255, null=True, blank=True)
    idn_node = models.ManyToManyField(IdnNode, null=True, blank=True)
    metadata_name= models.CharField(max_length=255)
    metadata_version = models.CharField(max_length=5)
    dif_creation_date = models.CharField(max_length=50, null=True, blank=True)
    last_dif_revision_date = models.CharField(max_length=50, null=True, blank=True)
    dif_revision_history = models.TextField(null=True, blank=True)
    future_dif_review_date = models.CharField(null=True, blank=True)
    private = models.CharField(max_length=10, null=True, blank=True)

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
    role = models.ManyToManyField(DatasetRole)
    first_name = models.OneToOneField(Person, null=True, blank=True)
    last_name = models.OneToOneField(Person)
    email= models.CharField(max_length=255, null=True, blank=True)
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

    def __str__(self):
        return "{} - {} - {}".format(self.category, self.topic, self.term)


class IsoTopicCategory(models.Model):
    uuid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.uuid)


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
    detailed_location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.location_subregion1)


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


class HorizontalResolutionRange(models.Model):
    uuid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.uuid)


class VerticalResolutionRange(models.Model):
    uuid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.uuid)


class TemporalResolutionRange(models.Model)
    uuid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.uuid)


class DataCenter(models.Model):
    data_center_name = models.ForeignKey(DataCenterName)
    data_set_id = models.CharField(max_length=255, null=True, blank=True)
    personnel = models.ManyToManyField(Personnel)

    def __str__(self):
        return "{}".format(self.data_center_name)


class DataCenterName(models.Model):
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.short_name)


class Distribution(models.Model):
    distribution_media = models.CharField(max_length=255, null=True, blank=True)
    distribution_size = models.CharField(max_length=255, null=True, blank=True)
    distribution_format = models.CharField(max_length=255, null=True, blank=True)
    fees = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{} {} {}".format(self.distribution_media, self.distribution_format, self.distribution_size)


class Summary(models.Model):
    abstract = models.TextField(null=True, blank=True)
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

    def __str__(self):
        return "{}".format(self.Horizontal_Resolution_Range)


class Instrument(models.Model):
    category = models.CharField(max_length=255, null=True, blank=True)
    class = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=255, null=True, blank=True)
    short_Name = models.CharField(max_length=255, null=True, blank=True)
    long_Name = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Short_Name)


class ScienceKeyword(models.Model):
    category = models.CharField(max_length=255, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    term = models.CharField(max_length=255, null=True, blank=True)
    variable_Level_1 = models.CharField(max_length=255, null=True, blank=True)
    variable_Level_2 = models.CharField(max_length=255, null=True, blank=True)
    variable_Level_3 = models.CharField(max_length=255, null=True, blank=True)
    detailed_Variable = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Term)


class Location(models.Model):
    location_Category = models.CharField(max_length=255, null=True, blank=True)
    location_Type = models.CharField(max_length=255, null=True, blank=True)
    location_Subregion1 = models.CharField(max_length=255, null=True, blank=True)
    location_Subregion2 = models.CharField(max_length=255, null=True, blank=True)
    location_Subregion3 = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{} - {} - {} - {}".format(self.Location_Category, self.Location_Type, self.Location_Subregion1, self.Location_Subregion2)


class Platform(models.Model):
    category = models.CharField(max_length=255, null=True, blank=True)
    series_Entity = models.CharField(max_length=255, null=True, blank=True)
    short_Name = models.CharField(max_length=255, null=True, blank=True)
    long_Name = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Short_Name)


class Project(models.Model):
    bucket = models.CharField(max_length=255, null=True, blank=True)
    short_Name = models.CharField(max_length=255, null=True, blank=True)
    long_Name = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Short_Name)


class Provider(models.Model):
    bucket_Level0 = models.CharField(max_length=255, null=True, blank=True)
    bucket_Level1 = models.CharField(max_length=255, null=True, blank=True)
    bucket_Level2 = models.CharField(max_length=255, null=True, blank=True)
    bucket_Level3 = models.CharField(max_length=255, null=True, blank=True)
    short_Name = models.CharField(max_length=255, null=True, blank=True)
    long_Name = models.CharField(max_length=255, null=True, blank=True)
    data_center_url = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Short_Name)


class RUContentType(models.Model):
    type = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Type)


class TemporalResolutionRange(models.Model):
    temporal_resolution_range = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Temporal_Resolution_Range)


class VerticalResolutionRange(models.Model):
    vertical_resolution_range = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    keyword_version = models.CharField(max_length=255, null=True, blank=True)
    keyword_revision_date = models.DateTimeField(null=True, blank=True)
    download_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.Vertical_Resolution_Range)










