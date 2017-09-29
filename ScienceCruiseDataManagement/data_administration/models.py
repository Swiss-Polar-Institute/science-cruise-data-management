from django.db import models
from main.models import Person, Project
import django.utils.timezone
from django.contrib.auth.models import User

# This file is part of https://github.com/Swiss-Polar-Institute/science-cruise-data-management

class PostCruiseDataContact(models.Model):
    person = models.ForeignKey(Person)
    project = models.ForeignKey(Project)
    system_user_created = models.BooleanField()
    created_on = models.DateTimeField(default=django.utils.timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        unique_together = (('person', 'project'),)

    def __str__(self):
        return "{}".format(self.person, self.project)

