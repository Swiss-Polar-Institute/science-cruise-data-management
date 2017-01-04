from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from data_storage_management.models import HardDisk, Directory, DirectoryImportLog
from django.views.decorators.csrf import csrf_exempt
import json

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

        directory.hard_disk = hard_disk
        directory.source_directory = relative_path
        directory.destination_directory = relative_path
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