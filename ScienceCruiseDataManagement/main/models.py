from django.db import models

# Create your models here.

class Event(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    event_number = models.IntegerField()
    time = models.DateTimeField()

    def __str__(self):
        return "{}".format(self.event_number)

class Project(models.Model):
    name=models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.name)