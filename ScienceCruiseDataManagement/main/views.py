import geojson
import json
from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView
from django.http import JsonResponse
from main.models import Event, Country
from django.utils import timezone

# Create your views here.
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


class EventsJson(View):
    def get(self, request):
        # print("-----------", request.GET['newer_than'])
        features = []
        for event in Event.objects.all():
            point = geojson.Point((event.longitude, event.latitude))

            features.append(
                geojson.Feature(geometry=point, properties={'id': str(event.event_number), 'text': 'this element'}))

        return JsonResponse(geojson.FeatureCollection(features))

class CountryListView(ListView):
    model = Country

    def get_context_data(self, **kwargs):
        context = super(CountryListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context