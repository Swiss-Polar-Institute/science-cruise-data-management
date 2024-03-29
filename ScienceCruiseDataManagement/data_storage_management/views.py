from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from data_storage_management.models import HardDisk, Directory, DirectoryImportLog
from django.views.decorators.csrf import csrf_exempt
import json

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

class DirectoryUpdateJson(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        directory_update = DirectoryImportLog()

        decoded_data = request.body.decode('utf-8')
        json_data = json.loads(decoded_data)
        directory_id = json_data['id']

        directory = Directory.objects.get(id=directory_id)

        directory_update.directory = directory
        directory_update.success = True

        directory.save()

        return JsonResponse({'status': 'ok'})


class HardDiskJson(View):
    @csrf_exempt
    def put(self, request, *args, **kwargs):
        decoded_data = request.body.decode('utf-8')
        json_data = json.loads(decoded_data)

        relative_path = json_data['relative_path']
        hard_disk_uuid = json_data['hard_disk_uuid']

        hard_disk = HardDisk()
        hard_disk.uuid = hard_disk_uuid

        directory = Directory()

        if not HardDisk.objects.filter(uuid=hard_disk_uuid).exists():
            hard_disk.save()
        else:
            hard_disk = HardDisk.objects.filter(uuid=hard_disk_uuid)[0]

        destination_directory = relative_path
        if not destination_directory.endswith("/"):
            destination_directory += "/"
        # This gets the last bit of the path (-2 because the path always ends with "/")
        destination_directory = destination_directory.split("/")[-2]

        directory.hard_disk = hard_disk
        directory.source_directory = relative_path
        directory.destination_directory = destination_directory
        directory.hard_disk = hard_disk

        if not Directory.objects.filter(destination_directory=relative_path).exists():
            directory.save()

        return JsonResponse({'status': 'ok'})

    def get(self, request_):
        hard_disk_uuid=request_.GET['hard_disk_uuid']

        try:
            hard_disk = HardDisk.objects.get(uuid=hard_disk_uuid)
        except: # TODO add exception type
            return JsonResponse({'error': 'hard disk not found', 'uuid': hard_disk_uuid})

        directories = []

        for directory in Directory.objects.filter(hard_disk=hard_disk):
            dir = {}
            dir['source'] = directory.source_directory
            dir['destination'] = directory.destination_directory
            dir['id'] = directory.pk
            directories.append(dir)

        information = {}

        information['uuid']=hard_disk.uuid
        information['label']=hard_disk.label
        if hard_disk.person:
            information['person']="{} {}".format(hard_disk.person.name_first, hard_disk.person.name_last)
        else:
            information['person'] = "NOT ASSIGNED, assign person to this hard disk on the admin please."
        information['comment']=hard_disk.comment
        information['directories'] = directories

        return JsonResponse(information)