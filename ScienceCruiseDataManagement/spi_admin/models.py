from django.db import models
import main.models

# Create your models here.

class MailingList(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return "{}".format(self.name)

    