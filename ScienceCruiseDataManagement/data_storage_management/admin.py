from django.contrib import admin
from data_storage_management import models
import data_storage_management.models


class HardDiskAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'label', 'person', 'comment', 'created_date_time')

    def directories_list(self, obj):
        result = []
        for directory in obj.directories.all():
            result.append(directory.path)

        return ",".join(result)


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('hard_disk', 'source_path', 'destination_path', 'created_date_time')


class DirectoryUpdatesAdmin(admin.ModelAdmin):
    list_display = ('directory', 'updated_time')

# Register your models here.
admin.site.register(data_storage_management.models.HardDisk, HardDiskAdmin)
admin.site.register(data_storage_management.models.Directory, DirectoryAdmin)
admin.site.register(data_storage_management.models.DirectoryUpdates, DirectoryUpdatesAdmin)