import glob
import json

import geojson
import os
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView, View, ListView
from django.core.exceptions import ObjectDoesNotExist

import main.import_gpx_to_stations
import main.models
from main import import_gpx_to_stations
from main.forms import InputShipDateTime
from main.models import Event, EventAction, Country, FilesStorage, FilesStorageGeneral, Port, Station, Message, ParentDevice
from main import utils
from ship_data.models import GpggaGpsFix, GpvtgVelocity


class MainMenuView(TemplateView):
    template_name = "main_menu.html"

    def get_context_data(self, **kwargs):
        context = super(MainMenuView, self).get_context_data(**kwargs)

        last_message = Message.objects.order_by('date_time')

        if len(last_message) == 0:
            message = "No message has been introduced yet, come back later"
            date_time = "N/A"
            person = "Data management team"
            subject = "No message"
        else:
            last_message = Message.objects.order_by('-date_time').first()
            message = last_message.message
            date_time = last_message.date_time
            person = last_message.person
            subject = last_message.subject

        now = utils.now_with_timezone()

        (position_latitude, position_longitude, position_date_time) = utils.latest_ship_position()

        context['message'] = message
        context['date_time'] = date_time
        context['person'] = person
        context['subject'] = subject
        context['date'] = now.strftime("%a %d %B %Y")
        context['time'] = now.strftime("%H:%M:%S")
        context['julian_day'] = now.strftime("%j")
        if position_latitude is not None:
            context['position_latitude'] = "{0:.4f}".format(position_latitude)
            context['position_longitude'] = "{0:.4f}".format(position_longitude)
            context['position_date_time'] = position_date_time
        else:
            context['position_latitude'] = "Unknown"
            context['position_longitude'] = "Unknown"
            context['position_date_time'] = "Unknown"

        speed = latest_ship_speed()

        if speed is not None:
            context['speed_kts'] = speed
        else:
            context['speed_kts'] = "Unknown"

        return context

class AccessingDataView(TemplateView):
    template_name = "accessing_data.html"

    def get_context_data(self, **kwargs):
        context = super(AccessingDataView, self).get_context_data(**kwargs)

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
            if eventAction.longitude is None or eventAction.latitude is None:
                continue

            point = geojson.Point((eventAction.longitude, eventAction.latitude))

            features.append(
                geojson.Feature(geometry=point, properties={'id': 'Event.{}'.format(eventAction.event.number),
                                                            'text': eventAction.general_comments,
                                                            'marker_color': 'blue'}))

        for port in Port.objects.all():
            if port.longitude is None or port.latitude is None:
                continue

            point = geojson.Point((port.longitude, port.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': 'Port.{}'.format(port.id),
                                                            'text': port.name,
                                                            'marker_color': 'yellow'}))

        for station in Station.objects.all():
            if station.longitude is None or station.latitude is None:
                continue

            point = geojson.Point((station.longitude, station.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': 'station.{}'.format(station.id),
                                                            'text': station.name,
                                                            'marker_color': 'green'}))

        (latest_ship_longitude, latest_ship_latitude, date_time_position) = utils.latest_ship_position()

        point = geojson.Point((latest_ship_longitude, latest_ship_latitude))

        features.append(
            geojson.Feature(geometry=point, properties={'id': 'ship',
                                                        'text': 'You are here',
                                                        'marker_color': 'orange'}))

        return JsonResponse(geojson.FeatureCollection(features))


class LastShipPosition(View):
    # simple view with only latitude, longitude and last ship position
    def get(self, request_):
        latest_ship_position = GpggaGpsFix.objects.latest("date_time")

        information = {}
        information['latitude'] = latest_ship_position.latitude
        information['longitude'] = latest_ship_position.longitude
        information['date_time'] = latest_ship_position.date_time

        return JsonResponse(information)


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
    units = "GB"

    def format_space_number(self, number):
        if self.units == "GB":
            conversion_from_kb = 1 / (1024 * 1024)  # How many context['units'] in one KB
            number *= conversion_from_kb
            return "{0:.2f}".format(number)
        else:
            raise

    def get_context_data(self, **kwargs):
        context = super(FileStorageView, self).get_context_data(**kwargs)
        context['file_storages'] = FilesStorage.objects.all()

        context['units'] = "GB"

        detailed_storage = []
        for storage in context['file_storages']:
            detailed_storage.append({'relative_path': str(storage.relative_path), context['units']: self.format_space_number(storage.kilobytes)})

        context['detailed_storage_json'] = json.dumps(detailed_storage)
        last_general_storage = FilesStorageGeneral.objects.latest('time')

        context['general_storage_free'] = self.format_space_number(last_general_storage.free)
        context['general_storage_used'] = self.format_space_number(last_general_storage.used)
        context['general_storage_size'] = self.format_space_number(last_general_storage.free + last_general_storage.used)
        context['general_storage_json'] = json.dumps({'used': self.format_space_number(last_general_storage.used), 'free': self.format_space_number(last_general_storage.free)})

        return context


class DocumentsView(TemplateView):
    template_name = "documents.html"

    def get_context_data(self, **kwargs):
        context = super(DocumentsView, self).get_context_data(**kwargs)
        documents = {}   # key: directory, values: files
                         # the key is a topic

        # Prepares a dictionary with the directory names as keys
        for file in glob.glob(os.path.join(settings.DOCUMENTS_DIRECTORY, "*")):
            if os.path.isdir(file):
                documents[os.path.basename(file)] = []

        # Adds a list of dictionary into each dictionary key with the title of the document and the link
        for topic in documents.keys():
            for file in glob.glob(os.path.join(settings.DOCUMENTS_DIRECTORY, os.path.join(settings.DOCUMENTS_DIRECTORY), topic, "*")):
                if os.path.isfile(file):
                    file_name = os.path.basename(file)
                    documents[topic].append(
                        {'title': file_name.split(".")[0],
                         'link': os.path.join('/documents_storage/{}/{}'.format(topic, file_name))
                         }
                    )

        context['documents'] = documents

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


class PositionFromDateTime(TemplateView):
    def get(self, request, *args, **kwargs):
        form = InputShipDateTime(initial={'ship_date_time': timezone.now})
        return render(request, "position_from_date_time.html", {'form': form})

    def post(self, request, *args, **kwargs):
        ship_date_time = request.POST['ship_date_time']
        form = InputShipDateTime(initial={'ship_date_time': ship_date_time})

        ship_date_time = utils.string_to_date_time(ship_date_time)

        if ship_date_time is None:
            position_date_time = "INVALID".format(ship_date_time)
            latitude = longitude = None
            message = "Invalid date time (format has to be YYYY-MM-DD HH:mm:SS) (or without the secs)"
        elif ship_date_time > utils.now_with_timezone():
            position_date_time = "FUTURE"
            latitude = longitude = None
            message = "The date time seems to be in the future. We don't know where we are going to be!"
        else:
            (latitude, longitude, position_date_time) = ship_position(ship_date_time)
            message = ''

        if latitude is None or longitude is None or position_date_time is None:
            latitude = longitude = "Unknown"
        else:
            latitude = "{0:.4f}".format(latitude)
            longitude = "{0:.4f}".format(longitude)

        template_information = {
            'ship_date_time': position_date_time,
            'latitude_decimal': latitude,
            'longitude_decimal': longitude,
            'form': form,
            'message': message
        }
        return render(request, "position_from_date_time_exec.html", template_information)


def ship_position(date_time):
    gps = ParentDevice.objects.all().get(name=settings.MAIN_GPS)
    position_main_gps_query = GpggaGpsFix.objects.all().filter(device=gps).filter(date_time__gt=date_time).order_by('date_time')
    position_any_gps_query = GpggaGpsFix.objects.all().filter(date_time__gt=date_time).order_by('date_time')

    if position_main_gps_query.exists():
        position_main_gps = position_main_gps_query[0]
        seconds_difference_main_gps = abs(date_time - position_main_gps.date_time).total_seconds()
    else:
        position_main_gps = None
        seconds_difference_main_gps = 99999

    if position_any_gps_query.exists():
        position_any_gps = position_any_gps_query[0]
        seconds_difference_any_gps = abs(date_time - position_any_gps.date_time).total_seconds()
    else:
        position_any_gps = None
        seconds_difference_any_gps = 99999

    if seconds_difference_main_gps < 60:
        position = position_main_gps
    elif seconds_difference_any_gps < 60:
        position = position_any_gps
    else:
        position = None

    if position is None:
        return (None, None, date_time)
    else:
        return (position.latitude, position.longitude, position.date_time)


def latest_ship_speed():
    try:
        gps = ParentDevice.objects.all().get(name="test")
    except ObjectDoesNotExist:
        return None

    velocities = GpvtgVelocity.objects.all().filter(device=gps).order_by('-date_time')

    if velocities.exists():
        speed = velocities[0]
        return speed.ground_speed_kts
    else:
        return None
