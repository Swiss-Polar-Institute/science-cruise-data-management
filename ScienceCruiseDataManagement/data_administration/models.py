from django.db import models
from main.models import Person, Project
import django.utils.timezone

# This file is part of https://github.com/Swiss-Polar-Institute/science-cruise-data-management

class PostCruiseDataContact(models.Model):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project)
    created_on = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        unique_together = (('person', 'project'),)

    def __str__(self):
        return "{}".format(self.person, self.project)

