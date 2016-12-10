import geojson
import json

from debug_toolbar.panels import request
from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView
from django.http import JsonResponse
from main.models import Event, Country, Storage, General_Storage, Position, PositionType
from django.utils import timezone


class MainMenuView(TemplateView):
    template_name = "main_menu.html"

    def get_context_data(self, **kwargs):
        context = super(MainMenuView, self).get_context_data(**kwargs)

        return context


class MainMapView(TemplateView):
    template_name = "main_map.html"

    def get_context_data(self, **kwargs):
        context = super(MainMapView, self).get_context_data(**kwargs)

        return context

class InteractiveMapView(TemplateView):
    template_name = "interactive_map.html"


    def get_context_data(self, **kwargs):
        context = super(InteractiveMapView, self).get_context_data(**kwargs)

        return context


class EventsJson(View):
    def get(self, request):
        # print("-----------", request.GET['newer_than'])
        features = []
        for event in Event.objects.all():
            point = geojson.Point((event.longitude, event.latitude))

            features.append(
                geojson.Feature(geometry=point, properties={'id': str(event.event_number), 'text': 'this element'}))

        return JsonResponse(geojson.FeatureCollection(features))

class PositionsJson(View):
    def get(self, request):
        # print("-----------", request.GET['newer_than'])
        features = []
        for position in Position.objects.order_by('number'):
            point = geojson.Point((position.longitude, position.latitude))

            text = position.text
            if text is None:
                text = ""

            features.append(
                geojson.Feature(geometry=point, properties={'id': position.id,
                                                            'number': position.number,
                                                            'text': text,
                                                            'type': position.position_type.name
                                                            }))

        return JsonResponse(geojson.FeatureCollection(features))

    def post(self, request):
        decoded_data = request.body.decode('utf-8')
        json_data = json.loads(decoded_data)

        # new POI to be inserted
        poi = Position()
        poi.latitude = json_data['latitude']
        poi.longitude = json_data['longitude']
        poi.position_type = PositionType.objects.get(name='Event')
        poi.save()

        print("POST",poi)

        return JsonResponse({'id': poi.id, 'text': poi.text})

    def put(self, request):
        decoded_data = request.body.decode('utf-8')
        json_data = json.loads(decoded_data)

        poi = Position.objects.get(id=json_data['id'])

        if 'latitude' in json_data:
            poi.latitude = json_data['latitude']

        if 'longitude' in json_data:
            poi.longitude = json_data['longitude']

        if 'text' in json_data:
            poi.text = json_data['text']

        poi.save()
        print("PUT ",poi)
        response = JsonResponse({'id': poi.id, 'text': poi.text})

        return response


class CountryListView(ListView):
    model = Country

    def get_context_data(self, **kwargs):
        context = super(CountryListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class StorageView(TemplateView):
    template_name = "storage.html"

    def get_context_data(self, **kwargs):
        context = super(StorageView, self).get_context_data(**kwargs)
        context['storages'] = Storage.objects.all()

        context['units'] = "KB"

        detailed_storage = []
        for storage in context['storages']:
            detailed_storage.append({'instrument': str(storage.instrument), context['units']: storage.kilobytes})

        context['detailed_storage_json'] = json.dumps(detailed_storage)
        last_general_storage = General_Storage.objects.latest('date')

        context['general_storage_free'] = last_general_storage.free
        context['general_storage_used'] = last_general_storage.used
        context['general_storage_size'] = context['general_storage_free'] + context['general_storage_used']
        context['general_storage_json'] = json.dumps({'used': last_general_storage.used, 'free': last_general_storage.free})

        return context

