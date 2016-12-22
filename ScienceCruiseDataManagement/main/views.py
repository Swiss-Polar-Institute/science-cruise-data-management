import geojson
import json

from debug_toolbar.panels import request
from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView
from django.http import JsonResponse

from main import import_gpx_to_stations
from main.models import Event, EventAction, Country, FilesStorage, FilesStorageGeneral, Port, Station, Message
from django.utils import timezone
from django.db.models import Q
import main.models
import main.import_gpx_to_stations

class MainMenuView(TemplateView):
    template_name = "main_menu.html"

    def get_context_data(self, **kwargs):
        context = super(MainMenuView, self).get_context_data(**kwargs)

        last_message = Message.objects.order_by('date_time')

        if len(last_message) == 0:
            message = "No message has been introduced yet, come back later"
            time = "N/A"
            person = "Data management team"
            subject = "No message"
        else:
            last_message = Message.objects.order_by('-date_time').first()
            message = last_message.message
            time = last_message.date_time
            person = last_message.person
            subject = last_message.subject

        context['message'] = message
        context['time'] = time
        context['person'] = person
        context['subject'] = subject

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


class PositionsJson(View):
    def get(self, request_):

        # Possibles colors: black, blue, green, grey, orange, red, violet, yellow

        tbegins = main.models.EventAction.tbegin()
        tinstant = main.models.EventAction.tinstant()

        features = []
        for eventAction in EventAction.objects.all().filter(Q(type=tbegins) | Q(type=tinstant)):
            point = geojson.Point((eventAction.longitude, eventAction.latitude))

            features.append(
                geojson.Feature(geometry=point, properties={'id': 'Event.{}'.format(eventAction.event.id),
                                                            'text': eventAction.general_comments,
                                                            'marker_color': 'blue'}))

        for port in Port.objects.all():
            point = geojson.Point((port.longitude, port.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': 'Port.{}'.format(port.id),
                                                            'text': port.name,
                                                            'marker_color': 'yellow'}))

        for station in Station.objects.all():
            point = geojson.Point((station.longitude, station.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': 'station.{}'.format(station.id),
                                                            'text': station.name,
                                                            'marker_color': 'green'}))


        return JsonResponse(geojson.FeatureCollection(features))

# class PositionsJson(View):
#     def get(self, request):
#         # print("-----------", request.GET['newer_than'])
#         features = []
#         for position in Position.objects.order_by('number'):
#             point = geojson.Point((position.longitude, position.latitude))
#
#             text = position.text
#             if text is None:
#                 text = ""
#
#             features.append(
#                 geojson.Feature(geometry=point, properties={'id': position.id,
#                                                             'number': position.number,
#                                                             'text': text,
#                                                             'type': position.position_type.name
#                                                             }))
#
#         return JsonResponse(geojson.FeatureCollection(features))
#
#     def post(self, request):
#         decoded_data = request.body.decode('utf-8')
#         json_data = json.loads(decoded_data)
#
#         # new POI to be inserted
#         poi = Position()
#         poi.latitude = json_data['latitude']
#         poi.longitude = json_data['longitude']
#         poi.position_type = PositionType.objects.get(name='Event')
#         poi.save()
#
#         print("POST",poi)
#
#         return JsonResponse({'id': poi.id, 'text': poi.text})
#
#     def put(self, request):
#         decoded_data = request.body.decode('utf-8')
#         json_data = json.loads(decoded_data)
#
#         poi = Position.objects.get(id=json_data['id'])
#
#         if 'latitude' in json_data:
#             poi.latitude = json_data['latitude']
#
#         if 'longitude' in json_data:
#             poi.longitude = json_data['longitude']
#
#         if 'text' in json_data:
#             poi.text = json_data['text']
#
#         poi.save()
#         print("PUT ",poi)
#         response = JsonResponse({'id': poi.id, 'text': poi.text})
#
#         return response


class CountryListView(ListView):
    model = Country

    def get_context_data(self, **kwargs):
        context = super(CountryListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class EventListView(ListView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['event_list'] = Event.objects.all()
        print(Event.objects.all()[0])
        return context


class FileStorageView(TemplateView):
    template_name = "file_storage.html"

    def get_context_data(self, **kwargs):
        context = super(FileStorageView, self).get_context_data(**kwargs)
        context['file_storages'] = FilesStorage.objects.all()

        context['units'] = "KB"

        detailed_storage = []
        for storage in context['file_storages']:
            detailed_storage.append({'relative_path': str(storage.relative_path), context['units']: storage.kilobytes})

        context['detailed_storage_json'] = json.dumps(detailed_storage)
        last_general_storage = FilesStorageGeneral.objects.latest('time')

        context['general_storage_free'] = last_general_storage.free
        context['general_storage_used'] = last_general_storage.used
        context['general_storage_size'] = context['general_storage_free'] + context['general_storage_used']
        context['general_storage_json'] = json.dumps({'used': last_general_storage.used, 'free': last_general_storage.free})

        return context


class ImportPortsFromGpx(View):

    def get(self, request, *args, **kwargs):
        return render(request, "import_ports_from_gpx_form.html")

    def post(self, request, *args, **kwargs):
        file = request.FILES['gpxfile']
        file_name = file.name
        file_content = file.read().decode('utf-8')

        (created, modified, skipped, reports) = import_gpx_to_stations.import_gpx_to_stations(file_content)

        template_information = {
            'created': created,
            'modified': modified,
            'skipped': skipped,
            'reports': reports,
            'file_name': file_name
        }

        return render(request, "import_ports_from_gpx_exec.html", template_information)
