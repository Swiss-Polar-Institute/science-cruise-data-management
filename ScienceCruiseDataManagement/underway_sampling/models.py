from django.db import models
from main.models import Project
from django.contrib import admin
import underway_sampling.models

# Note that the script that enters data into these database tables may no longer work because additional fields have been added to the tables.

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

# Create your models here.
class UnderwaySamplingVariable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class When(models.Model):
    frequency = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.frequency

class UnderwaySampling(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    when = models.ManyToManyField(When)
    what = models.ManyToManyField(UnderwaySamplingVariable)
