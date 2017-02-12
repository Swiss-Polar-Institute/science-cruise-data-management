from django.shortcuts import render
from django.views.generic import TemplateView
from ship_data.models import Ferrybox
from django.db.models import Q
from django.forms.models import model_to_dict
from main import utils

import datetime
import json

class FerryboxView(TemplateView):
    def get(self, request, *args, **kwargs):
        latest_information = Ferrybox.objects.latest()
        temperatures = get_ferrybox_data_24_hours('temperature')
        salinities = get_ferrybox_data_24_hours('salinity')
        fluorimeters = get_ferrybox_data_24_hours('fluorimeter')

        now_utc = utils.set_utc(datetime.datetime.utcnow())

        latest_information_minutes_ago = int((now_utc - latest_information.date_time).seconds / 60)

        return render(request, "ferrybox.html", {"latest_information": latest_information,
                                                 "latest_information_minutes_ago": latest_information_minutes_ago,
                                                 "temperatures": json.dumps(temperatures),
                                                 "salinities": json.dumps(salinities),
                                                 "fluorimeter": json.dumps(fluorimeters)
                                                 }
                      )

def get_ferrybox_data_24_hours(field):
    result = []
    latest_data = Ferrybox.objects.latest()
    start_time = utils.set_utc(latest_data.date_time)
    end_time = utils.set_utc(latest_data.date_time - datetime.timedelta(days=1))
    delta_time = datetime.timedelta(minutes=10)
    current_time = latest_data.date_time

    while current_time > end_time:
        d = {}
        d['x'] = -((start_time - current_time).seconds/3600)
        ferrybox = Ferrybox.objects.filter(Q(date_time__lte=current_time)).order_by('-date_time')

        if not ferrybox.exists():
            break

        ferrybox = model_to_dict(ferrybox[0])
        d['y'] = ferrybox[field]

        result.append(d)
        current_time -= delta_time

    return result