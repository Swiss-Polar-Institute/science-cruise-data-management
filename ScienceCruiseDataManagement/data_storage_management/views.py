from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from data_storage_management.models import HardDisk, Directory, DirectoryUpdates
from django.views.decorators.csrf import csrf_exempt
import json

class DirectoryUpdateJson(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        directory_update = DirectoryUpdates()

        decoded_data = request.body.decode('utf-8')
        json_data = json.loads(decoded_data)
        directory_id = json_data['id']

        directory = Directory.objects.all().get(id=directory_id)

        directory_update.directory = directory

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

        if not HardDisk.objects.all().filter(uuid=hard_disk_uuid).exists():
            hard_disk.save()
        else:
            hard_disk = HardDisk.objects.all().filter(uuid=hard_disk_uuid)[0]

        directory.hard_disk = hard_disk
        directory.source_path = relative_path
        directory.destination_path = relative_path
        directory.hard_disk = hard_disk

        if not Directory.objects.all().filter(destination_path=relative_path).exists():
            directory.save()

        return JsonResponse({'status': 'ok'})

    def get(self, request_):
        hard_disk_uuid=request_.GET['hard_disk_uuid']

        try:
            hard_disk = HardDisk.objects.all().get(uuid=hard_disk_uuid)
        except: # TODO add exception time
            return JsonResponse({'error': 'hard disk not found', 'uuid': hard_disk_uuid})

        directories = []

        for directory in Directory.objects.all().filter(hard_disk=hard_disk):
            dir = {}
            dir['source'] = directory.source_path
            dir['destination'] = directory.destination_path
            dir['id'] = directory.pk
            directories.append(dir)

        information = {}

        information['uuid']=hard_disk.uuid
        information['label']=hard_disk.label
        information['person']="{} {}".format(hard_disk.person.name_first, hard_disk.person.name_last)
        information['comment']=hard_disk.comment
        information['directories'] = directories

        return JsonResponse(information)