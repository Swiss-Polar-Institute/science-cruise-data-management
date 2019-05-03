import glob
import json
import datetime

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
from main.forms import InputShipDateTime, InputCoordinates, InputShipTimes
from main.models import Event, EventAction, Country, FilesStorage, FilesStorageGeneral, Port, Station,\
    Message, SamplingMethod, ProposedStation, Leg, Depth, Sample, Person, ContactDetails
from ctd.models import CtdSampleVolume
from main import utils
from ship_data.models import GpggaGpsFix, GpvtgVelocity
import main.find_locations as find_locations
import subprocess
import main.utils_coordinates as utils_coordinates
from django.views.static import serve
from django.db.models import Sum
import geojson

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


def calculate_km_travelled():
    fp = open(settings.TRACK_MAP_FILEPATH)

    g = geojson.load(fp)

    previous = None
    distance = 0
    for item in g.get('coordinates'):
        if previous is not None:
            distance += utils_coordinates.calculate_distance((previous[1], previous[0]), (item[1], item[0]))

        previous = item

    return distance

def people_in_leg(number):
    return Person.objects.filter(leg=Leg.objects.get(number=number)).count()

class StatsView(TemplateView):
    template_name = "stats.html"

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)

        context['number_of_samples'] = Sample.objects.all().count()
        context['number_of_events'] = Event.objects.filter(outcome="success").count()
        context['litres_of_ctd_water'] = int(CtdSampleVolume.objects.all().aggregate(Sum('volume'))['volume__sum'])
        context['km_travelled'] = int(calculate_km_travelled())
        context['people_leg1'] = people_in_leg(1)
        context['people_leg2'] = people_in_leg(2)
        context['people_leg3'] = people_in_leg(3)
        context['people_all_legs'] = Person.objects.\
            filter(leg=Leg.objects.get(number=1)).\
            filter(leg=Leg.objects.get(number=2)).\
            filter(leg=Leg.objects.get(number=3)).count()
        context['terrestial_sites'] = 13
        context['most_southerly_point'] = "-74.009 -127.475"

        return context

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

        location = utils.latest_ship_position()

        context['message'] = message
        context['date_time'] = date_time
        context['person'] = person
        context['subject'] = subject
        context['date'] = now.strftime("%a %d %B %Y")
        context['time'] = now.strftime("%H:%M:%S")
        context['julian_day'] = now.strftime("%j")
        if location.latitude is not None:
            context['position_latitude'] = "{0:.4f}".format(location.latitude)
            context['position_longitude'] = "{0:.4f}".format(location.longitude)
            context['position_date_time'] = location.date_time
        else:
            context['position_latitude'] = "Unknown"
            context['position_longitude'] = "Unknown"
            context['position_date_time'] = "Unknown"

        speed = latest_ship_speed()

        if speed is not None:
            context['speed_kts'] = speed
        else:
            context['speed_kts'] = "Unknown"

        depths = Depth.objects.filter(depth__gt=0).order_by('-date_time')

        if depths.exists():
            depth = depths[0].depth
            time1 = utils.set_utc(datetime.datetime.now())
            time2 = utils.set_utc(depths[0].date_time)
            depth_updated_seconds_ago = (time1-time2).seconds
        else:
            depth = "Unknown"
            depth_updated_seconds_ago = "Unknown"

        context['depth'] = depth
        context['depth_updated_seconds_ago'] = depth_updated_seconds_ago

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


class TrackJson(View):
    def get(self, request_):
        track = open(settings.TRACK_MAP_FILEPATH, "r")
        return JsonResponse(json.load(track))


class PositionsJson(View):
    def get(self, request_):

        # Possibles colors: black, blue, green, grey, orange, red, violet, yellow
        tbegins = main.models.EventAction.tbegin()
        tinstant = main.models.EventAction.tinstant()

        features = []
        for eventAction in EventAction.objects.filter(Q(type=tbegins) | Q(type=tinstant)):
            if eventAction.longitude is None or eventAction.latitude is None:
                continue

            point = geojson.Point((eventAction.longitude, eventAction.latitude))


            link = '<a href="/admin/main/eventaction/{}/change/">{}</a>'.format(eventAction.id, eventAction.event.number)
            id_text = "Event: {}".format(link)

            date_time = eventAction.time.strftime("%Y-%m-%d %H:%M")

            features.append(
                geojson.Feature(geometry=point, properties={'id': id_text,
                                                            'text': "{}<br>{}<br>({:.2f}, {:.2f})".format(eventAction.event.sampling_method.name, date_time, eventAction.latitude, eventAction.longitude),
                                                            'marker_color': 'blue'}))

        for port in Port.objects.all():
            if port.longitude is None or port.latitude is None:
                continue

            point = geojson.Point((port.longitude, port.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': 'Port.{}'.format(port.id),
                                                            'text': port.name,
                                                            'marker_color': 'yellow'}))

        for proposedstation in ProposedStation.objects.all():
            if proposedstation.longitude is None or proposedstation.latitude is None:
                continue

            point = geojson.Point((proposedstation.longitude, proposedstation.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': 'Planned station',
                                                            'text': "{}<br>{}<br>({:.2f}, {:.2f})".format(proposedstation.name, proposedstation.comment, proposedstation.latitude, proposedstation.longitude),
                                                            'marker_color': 'red'}))


        for station in Station.objects.all():
            if station.longitude is None or station.latitude is None:
                continue

            link = '<a href="/admin/main/station/{}/change/">{}</a>'.format(station.name, station.name)
            id_text = "Station: {}".format(link)

            if station.arrival_time is not None:
                date_time = station.arrival_time.strftime("%Y-%m-%d %H:%M")
            else:
                date_time = "Unknown arrival datetime"

            point = geojson.Point((station.longitude, station.latitude))
            features.append(
                geojson.Feature(geometry=point, properties={'id': '{}'.format(id_text),
                                                            'text': "Type: {}<br>{}<br>({:.2f}, {:.2f})".format(station.type, date_time, station.latitude, station.longitude),
                                                            'marker_color': 'green'}))

        location = utils.latest_ship_position()

        point = geojson.Point((location.longitude, location.latitude))

        features.append(
            geojson.Feature(geometry=point, properties={'id': 'ship',
                                                        'text': 'You are here',
                                                        'marker_color': 'orange'}))

        return JsonResponse(geojson.FeatureCollection(features))


class LatestShipPosition(View):
    # simple view with only latitude, longitude and last ship position
    def get(self, request_):
        location = utils.latest_ship_position()

        information = {}
        information['latitude'] = location.latitude
        information['longitude'] = location.longitude
        information['date_time'] = location.date_time

        return JsonResponse(information)


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
            raise NotImplementedError

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
        documents = []
        directories = []

        # Prepares a dictionary with the directory names as keys
        for file in glob.glob(os.path.join(settings.DOCUMENTS_DIRECTORY, "*")):
            if os.path.isdir(file):
                directories.append(os.path.basename(file))


        for directory in directories:
            for file in glob.glob(os.path.join(settings.DOCUMENTS_DIRECTORY, os.path.join(settings.DOCUMENTS_DIRECTORY), directory, "*")):
                if os.path.isfile(file):
                    file_name = os.path.basename(file)
                    if file_name == "Thumbs.db":
                        continue

                    document = {}
                    document['title'] = file_name.split(".")[0]
                    document['link'] = os.path.join('/documents_storage/{}/{}'.format(directory, file_name))
                    document['topic'] = directory

                    documents.append(document)

        context['documents'] = documents
        context['topics'] = sorted(directories)

        return context


class CoordinatesConversion(TemplateView):
    def get(self, request, *args, **kwargs):
        form = InputCoordinates()
        return render(request, "coordinates_conversion.html", {"form": form})

    def post(self, request, *args, **kwargs):
        coordinates = request.POST['coordinates']

        form = InputCoordinates(initial={'coordinates': coordinates})

        template_information = {}
        template_information['form'] = form

        utils_coordinates.process(coordinates, template_information)

        return render(request, "coordinates_conversion_exec.html", template_information)


class PositionFromDateTime(TemplateView):
    def get(self, request, *args, **kwargs):
        form = InputShipDateTime(initial={'ship_date_time': timezone.now})
        return render(request, "position_from_date_time.html", {'form': form})

    def post(self, request, *args, **kwargs):
        ship_date_time = request.POST['ship_date_time']
        ship_date_times = request.POST['ship_date_times']

        form = InputShipDateTime(initial={'ship_date_time': ship_date_time,
                                          'ship_date_times': ship_date_times})

        template_information = find_locations.find_locations(ship_date_time, ship_date_times)
        template_information['form'] = form

        return render(request, "position_from_date_time_exec.html", template_information)


class ShipTimeToUtc(TemplateView):
    def get(self, request, *args, **kwargs):
        form = InputShipTimes(initial={'ship_date_times': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")})
        return render(request, "ship_time_to_utc.html", {'form': form})

    def post(self, request, *args, **kwargs):
        ship_date_times = request.POST['ship_date_times']

        form = InputShipTimes(initial={'ship_date_times': ship_date_times})

        template_information = {}
        template_information['times'] = ship_date_times_to_utc(ship_date_times)
        template_information['form'] = form

        return render(request, "ship_time_to_utc_exec.html", template_information)


class MailState(TemplateView):
    def get(self, request, *args, **kwargs):
        s = subprocess.Popen("mailq", stdout=subprocess.PIPE)
        mails = s.stdout.read()

        return render(request, "mail_state.html", {'mails': mails})


class LatestImage(View):
    def get(self, request):
        filepath = settings.IMAGE_RELOAD_FILEPATH
        return serve(request, os.path.basename(filepath), os.path.dirname(filepath))


class ImageReloaderView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, "image_reloader.html")


def latest_ship_speed():
    try:
        gps = SamplingMethod.objects.get(name=settings.MAIN_GPS)
    except ObjectDoesNotExist:
        return None

    velocities = GpvtgVelocity.objects.filter(device=gps).order_by('-date_time')

    if velocities.exists():
        speed = velocities[0]
        return speed.ground_speed_kts
    else:
        return None

def ship_date_times_to_utc(ship_date_times):
    output = []
    for ship_date_time in ship_date_times.split("\n"):
        ship_date_time = ship_date_time.strip()
        try:
            date_time = datetime.datetime.strptime(ship_date_time, "%Y-%m-%d %H:%M:%S")

            message = ""
            if date_time.date() == settings.DATE_TWO_DAYS.date():
                message = "We had two days with the same date, unknown UTC"

            elif date_time > datetime.datetime.now() + datetime.timedelta(days=1):
                message = "Don't ask about the future..."

            elif utils.set_utc(date_time) < Leg.objects.all().order_by("start_time")[0].start_time:
                # This is an approximation - due to the timezones
                message = "Don't ask about before the beginning of the voyage"

            if message != "":
                output.append({'ship_date_time': ship_date_time,
                               'utc_date_time': message,
                               'utc_julian_day': message
                               })
                continue
            ship_ahead_of_utc = main.models.TimeChange.objects.filter(Q(date_changed_utc__lte=date_time)).order_by('-date_changed_utc')
            if len(ship_ahead_of_utc) > 0:
                ship_ahead_of_utc_hours = int(ship_ahead_of_utc[0].difference_to_utc_after_change)

                ahead_of_utc = datetime.timedelta(hours=ship_ahead_of_utc_hours)

                date_time_utc = date_time - ahead_of_utc
            else:
                date_time_utc = "Unknown"

            utc_julian_day = date_time_utc.strftime("%j")

        except ValueError:
            date_time_utc = '<p style="color:red"><b>Date in invalid format</b></p>'
            utc_julian_day = '<p style="color:red"><b>Date in invalid format</b></p>'

        output.append({'ship_date_time': ship_date_time,
                       'utc_date_time': date_time_utc,
                       'utc_julian_day': utc_julian_day
                       })

    return output