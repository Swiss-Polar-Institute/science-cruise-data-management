from django.contrib import admin
from data_storage_management import models
import data_storage_management.models


class HardDiskAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'label', 'person', 'comment', 'added_date_time')

    def directories_list(self, obj):
        result = []
        for directory in obj.directories.all():
            result.append(directory.path)

        return ",".join(result)


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('hard_disk', 'source_path', 'destination_path', 'added_date_time')


class DirectoryFile(admin.ModelAdmin):
    list_display = ('hard_disk', 'source_path', 'destination_path', 'added_date_time')


class DirectoryUpdatesAdmin(admin.ModelAdmin):
    list_display = ('directory', 'updated_time')


class NASDirectoryAdmin(admin.ModelAdmin):
    list_display = ('shared_resource', 'added_date_time', 'comment')


class SharedResourceAdmin(admin.ModelAdmin):
    list_display = ('ip', 'shared_resource', 'added_date_time', 'person', 'comment', 'username', 'password')


# Register your models here.
admin.site.register(data_storage_management.models.HardDisk, HardDiskAdmin)
admin.site.register(data_storage_management.models.Directory, DirectoryAdmin)
admin.site.register(data_storage_management.models.File, DirectoryFile)
admin.site.register(data_storage_management.models.DirectoryUpdates, DirectoryUpdatesAdmin)
admin.site.register(data_storage_management.models.NASDirectory, NASDirectoryAdmin)
admin.site.register(data_storage_management.models.SharedResource, SharedResourceAdmin)