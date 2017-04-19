from django.contrib import admin
from data_storage_management import models
from main.models import Person
import data_storage_management.models

# This file is part of https://github.com/cpina/science-cruise-data-management
#
# This project was programmed in a hurry without any prior Django experience,
# while circumnavigating the Antarctic on the ACE expedition, without proper
# Internet access, with 150 scientists using the system and doing at the same
# cruise other data management and system administration tasks.
#
# Sadly there aren't unit tests and we didn't have time to refactor the code
# during the cruise, which is really needed.
#
# Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk), 2016-2017.

class HardDiskAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'label', 'person', 'comment', 'added_date_time')

    def directories_list(self, obj):
        result = []
        for directory in obj.directories.all():
            result.append(directory.path)

        return ",".join(result)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('source_directory', 'destination_directory', 'added_date_time', 'hard_disk', 'shared_resource', 'nas_resource', 'backup_disabled', )


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
admin.site.register(data_storage_management.models.File, ItemAdmin)
admin.site.register(data_storage_management.models.DirectoryImportLog, DirectoryImportLog)
admin.site.register(data_storage_management.models.NASResource, NASResourceAdmin)
admin.site.register(data_storage_management.models.SharedResource, SharedResourceAdmin)
admin.site.register(data_storage_management.models.DataManagementProgress, DataManagementProgressAdmin)