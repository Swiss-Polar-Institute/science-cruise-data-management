from django.db import models
from main.models import Project
from django.contrib import admin
import underway_sampling.models

# Create your models here.
class UnderwaySamplingVariable(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class When(models.Model):
    frequency = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.frequency

class UnderwaySampling(models.Model):
    project = models.ForeignKey(Project)
    when = models.ManyToManyField(When)
    what = models.ManyToManyField(UnderwaySamplingVariable)
