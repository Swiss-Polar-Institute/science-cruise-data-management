from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from data_storage_management.models import HardDisk, Directory

class HardDiskJson(View):
    def put(self, request, *args, **kwargs):
        d = {'name': 'carles'}
        return JsonResponse(d)

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
            directories.append(dir)

        information = {}

        information['uuid']=hard_disk.uuid
        information['label']=hard_disk.label
        information['person']="{} {}".format(hard_disk.person.name_first, hard_disk.person.name_last)
        information['comment']=hard_disk.comment
        information['directories'] = directories

        return JsonResponse(information)