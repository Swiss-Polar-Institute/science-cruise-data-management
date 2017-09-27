from django.db import models
from main.models import Project
from main.models import Person
from main.models import Organisation
import django.utils.timezone
from django.contrib.auth.models import User

# This application contains information that has been reported by the expedition participants.
class AudienceSize(models.Model):
    number_people = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.number_people)


class AudienceType(models.Model):
    type = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.type)


class MediaType(models.Model):
    type = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}".format(self.type)


class OutreachActivity(models.Model):
    project = models.ManyToManyField(Project, help_text="Please select the project(s) to which your outreach activity was related. If it was about the expedition in general, please select all projects.")
    person = models.ManyToManyField(Person, help_text="Please enter the people that were involved in your outreach activity. If they are not listed here, please add them to the database.")
    activity_date = models.DateField(help_text="Please enter the date on which your activity took place.")
    activity_title = models.TextField(help_text="Please give the title of your outreach activity.")
    activity_description = models.TextField(help_text="Please give a brief description of your activity. Please complete the information in the other fields if there is a suitable space to put it.")
    activity_location_event = models.CharField(max_length=255, help_text="Please give the name of the event at which your outreach activity took place, if applicable.", blank=True, null=True)
    activity_location_event_link = models.TextField(help_text="Please give a weblink to the outreach activity if available.", blank=True, null=True)
    activity_location_organisation = models.ManyToManyField(Organisation, help_text="Please list the organisation(s) at which the outreach activity took place.")
    audience_size = models.ForeignKey(AudienceSize, help_text="Please estimate the size of the audience reached by your outreach activity.")
    audience_type = models.ManyToManyField(AudienceType, help_text="Please give an idea of the type of audience at which your activity was aimed.")
    media_type = models.ManyToManyField(MediaType, help_text="Please select the main types of media used during your outreach activity.")
    link = models.TextField(blank=True, null=True, help_text="Please enter the weblink the outreach material if available. If this is a DOI, please enter it in the Outreach DOI name field.")
    outreach_doi_name = models.CharField(max_length=255, blank=True, null=True, help_text="Please enter the DOI name of the outreach activity if applicable.")
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.activity_title)