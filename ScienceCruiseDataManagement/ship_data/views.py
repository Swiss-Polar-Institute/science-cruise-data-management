from django.shortcuts import render
from django.views.generic import TemplateView
from ship_data.models import Ferrybox

import datetime

class FerryboxView(TemplateView):
    def get(self, request, *args, **kwargs):
        latest_information = Ferrybox.objects.latest()
        # temperatures = get_ferrybox_temperatures()
        return render(request, "ferrybox.html", {"latest_information": latest_information})


def get_ferrybox_temperatures():
    latest_temperature = Ferrybox.objects.latest()

    one_hour = datetime.timedelta(hours=1)
    current_time = latest_temperature

    for last_hours in range(0, 24):
        d = {}
        d['x'] = last_hours
        d['y'] = ferrybox_data('temperature', current_time)

        current_time -= one_hour

def ferrybox_data():
    pass


# Create your views here.
