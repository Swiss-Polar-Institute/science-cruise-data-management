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


class ItemAdmin(admin.ModelAdmin):
    list_display = ('source_directory', 'destination_directory', 'added_date_time', 'hard_disk', 'shared_resource', 'nas_resource')


class DirectoryUpdatesAdmin(admin.ModelAdmin):
    list_display = ('directory', 'updated_time')


class NASResourceAdmin(admin.ModelAdmin):
    list_display = ('shared_resource', 'added_date_time', 'comment')


class SharedResourceAdmin(admin.ModelAdmin):
    list_display = ('ip', 'shared_resource', 'added_date_time', 'person', 'comment', 'username', 'password')


# Register your models here.
admin.site.register(data_storage_management.models.HardDisk, HardDiskAdmin)
admin.site.register(data_storage_management.models.Directory, ItemAdmin)
admin.site.register(data_storage_management.models.File, ItemAdmin)
admin.site.register(data_storage_management.models.DirectoryUpdates, DirectoryUpdatesAdmin)
admin.site.register(data_storage_management.models.NASResource, NASResourceAdmin)
admin.site.register(data_storage_management.models.SharedResource, SharedResourceAdmin)