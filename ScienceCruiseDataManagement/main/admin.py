from django.contrib import admin

from main.models import Project
from main.models import Event
from main.models import Country

# Register your models here.
# admin.site.register(Project)
admin.site.register(Event)
admin.site.register(Country)

class ProjectsStartsWithA(admin.SimpleListFilter):
    title = "Projects starts with A"
    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        return (('a', 'Starts with A'),
                ('b', 'Starts with B'))

    def queryset(self, request, queryset):
        if self.value() == 'a':
            return queryset.filter(name__startswith='a')

        if self.value() == 'b':
            return queryset.filter(name__startswith='b')

class ProjectAdmin(admin.ModelAdmin):
    # list_filter = ('name')
    list_display = ('name', 'country')
    list_filter = (ProjectsStartsWithA, )


admin.site.register(Project, ProjectAdmin)