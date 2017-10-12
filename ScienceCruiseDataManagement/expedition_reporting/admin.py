from django.contrib import admin
from django.forms import ModelMultipleChoiceField
import expedition_reporting.models
import import_export
from main.admin_filters import ProjectFilter, PersonFilter


class AudienceSizeAdmin(admin.ModelAdmin):
    list_display = ('number_people', 'description')
    ordering = ['number_people']
    search_fields = ('number_people',)


class AudienceTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'description')
    ordering = ['type']
    search_fields = ('type',)


class MediaTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'description')
    ordering = ['type']
    search_fields = ('type',)


class OutreachActivityAdmin(import_export.admin.ExportMixin, admin.ModelAdmin):
    list_display = ('activity_title', 'project_list', 'person_list', 'activity_date', 'activity_description', 'activity_location_event', 'activity_location_event_link',
                    'activity_location_organisation_list', 'audience_size', 'audience_type_list', 'media_type_list', 'link', 'outreach_doi_name', 'created_on', 'created_by')
    list_filter = (ProjectFilter, PersonFilter,)
    ordering = ['project', 'person', 'activity_title', 'media_type', 'audience_size', 'audience_type']
    search_fields = ('project', 'person', 'activity_title', 'media_type', 'audience_size', 'audience_type')
    filter_vertical = ('project', 'person')
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.save()

    def project_list(self, obj):
        projects = obj.project.all()

        return ",".join([str(project) for project in projects])

    def person_list(self, obj):
        people = obj.person.all()

        return ",".join([str(person) for person in people])

    def activity_location_organisation_list(self, obj):
        activity_location_organisations = obj.activity_location_organisation.all()

        return ",".join([str(activity_location_organisation) for activity_location_organisation in activity_location_organisations])

    def audience_type_list(self, obj):
        audience_types = obj.audience_type.all()

        return ",".join([str(audience_type) for audience_type in audience_types])

    def media_type_list(self, obj):
        media_types = obj.media_type.all()

        return ",".join([str(media_type) for media_type in media_types])


admin.site.register(expedition_reporting.models.AudienceSize, AudienceSizeAdmin)
admin.site.register(expedition_reporting.models.AudienceType, AudienceTypeAdmin)
admin.site.register(expedition_reporting.models.MediaType, MediaTypeAdmin)
admin.site.register(expedition_reporting.models.OutreachActivity, OutreachActivityAdmin)
