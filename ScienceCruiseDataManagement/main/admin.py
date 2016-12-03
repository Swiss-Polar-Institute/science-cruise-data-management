from django.contrib import admin

from main.models import Project
from main.models import Event

# Register your models here.
admin.site.register(Project)
admin.site.register(Event)