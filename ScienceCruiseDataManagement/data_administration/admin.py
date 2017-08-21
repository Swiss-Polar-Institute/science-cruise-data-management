from django.contrib import admin
import data_administration.models


class PostCruiseDataContactAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'created_on')

# Register your models here.
admin.site.register(data_administration.models.PostCruiseDataContact, PostCruiseDataContactAdmin)