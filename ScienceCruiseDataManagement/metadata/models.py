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

# Create your models here.

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
    data_set_progress = models.ForeignKey(DataSetProgress, null=True, blank=True)
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

class Data_Set_Citation(models.Model):
    dataset_creator = models.ForeignKey(Person, null=True, blank=True)
    dataset_title = models.CharField(max_length=255, null=True, blank=True)
    dataset_release_date = models.DateField(null=True,blank=True)
    dataset_publisher = models.ForeignKey(Organisation, null=True, blank=True)
    version = models.CharField(max_length=10, null=True, blank=True)
    other_citation_details = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.dataset_title)

