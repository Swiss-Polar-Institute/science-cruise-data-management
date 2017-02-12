from django.shortcuts import render
from django.views.generic import TemplateView
from ship_data.models import Ferrybox
from django.db.models import Q
from django.forms.models import model_to_dict

import datetime
import json

class FerryboxView(TemplateView):
    def get(self, request, *args, **kwargs):
        latest_information = Ferrybox.objects.latest()
        temperatures = get_ferrybox_data_24_hours('temperature')
        salinities = get_ferrybox_data_24_hours('salinity')
        fluorimeters = get_ferrybox_data_24_hours('fluorimeter')

        return render(request, "ferrybox.html", {"latest_information": latest_information,
                                                 "temperatures": json.dumps(temperatures),
                                                 "salinities": json.dumps(salinities),
                                                 "fluorimeters": json.dumps(fluorimeters)
                                                 }
                      )

def get_ferrybox_data_24_hours(field):
    result = []
    latest_data = Ferrybox.objects.latest()

    one_hour = datetime.timedelta(hours=1)
    current_time = latest_data.date_time

    for last_hours in range(0, 24):
        d = {}
        d['x'] = -last_hours
        ferrybox = Ferrybox.objects.filter(Q(date_time__lt=current_time)).order_by('-date_time')

        if not ferrybox.exists():
            break

        ferrybox = model_to_dict(ferrybox[0])
        d['y'] = ferrybox[field]

        result.append(d)
        current_time -= one_hour

    return result