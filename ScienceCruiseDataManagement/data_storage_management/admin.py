from django.contrib import admin
from data_storage_management import models
from main.models import Person
import data_storage_management.models


class HardDiskAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'label', 'person', 'comment', 'added_date_time')

    def directories_list(self, obj):
        result = []
        for directory in obj.directories.all():
            result.append(directory.path)

        return ",".join(result)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('source_directory', 'destination_directory', 'added_date_time', 'hard_disk', 'shared_resource', 'nas_resource', 'source_instrument_list')

    def source_instrument_list(self, obj):
        result = []
        for instrument in obj.source_instrument.all():
            result.append("{} - {}".format(instrument.type_of_device.full_name, instrument.identifying_mark))

        return ", ".join(result)

class DirectoryImportLog(admin.ModelAdmin):
    list_display = ('directory', 'updated_time', 'success')


class NASResourceAdmin(admin.ModelAdmin):
    list_display = ('shared_resource', 'added_date_time', 'comment')


class SharedResourceAdmin(admin.ModelAdmin):
    list_display = ('ip', 'shared_resource', 'added_date_time', 'person', 'comment', 'username', 'password')


class DataManagementProgressAdmin(admin.ModelAdmin):
    list_display = ('project', 'leg', 'event_recording', 'events_complete', 'sample_recording', 'samples_complete', 'metadata_record', 'data_management_plan',  'data_contact_list', 'last_updated')
    ordering = ['project']

    def data_contact_list(self, obj):
        people = obj.data_contact.all()

        result = ""
        for person in people:
            if result != "":
                result = result + ", "
            result = result + person.name_first + ' ' + person.name_last

        return result


# Register your models here.
admin.site.register(data_storage_management.models.HardDisk, HardDiskAdmin)
admin.site.register(data_storage_management.models.Directory, ItemAdmin)
admin.site.register(data_storage_management.models.ShipData, ItemAdmin)
admin.site.register(data_storage_management.models.File, ItemAdmin)
admin.site.register(data_storage_management.models.DirectoryImportLog, DirectoryImportLog)
admin.site.register(data_storage_management.models.NASResource, NASResourceAdmin)
admin.site.register(data_storage_management.models.SharedResource, SharedResourceAdmin)
admin.site.register(data_storage_management.models.DataManagementProgress, DataManagementProgressAdmin)