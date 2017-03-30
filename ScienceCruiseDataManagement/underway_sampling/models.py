from django.db import models
from main.models import Project
from django.contrib import admin
import underway_sampling.models

# Create your models here.
class UnderwaySamplingVariable(models.Model):
    name = models.CharField(max_length=255, unique=True)

class When(models.Model):
    frequency = models.CharField(max_length=255)
    comment = models.TextField()

class UnderwaySampling(models.Model):
    project = models.ForeignKey(Project)
    when = models.ManyToManyField(When)
    what = models.ManyToManyField(UnderwaySamplingVariable)