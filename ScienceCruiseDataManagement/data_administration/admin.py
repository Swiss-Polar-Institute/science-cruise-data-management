from django.contrib import admin
import data_administration.models


class PostCruiseDataContactAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'system_user_created', 'created_on', 'created_by')
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.save()

# Register your models here.
admin.site.register(data_administration.models.PostCruiseDataContact, PostCruiseDataContactAdmin)