import datetime
import json

from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from main import utils
from ship_data.models import Ferrybox, GpggaGpsFix


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

class GetPosition(View):
    @staticmethod
    def get_closest_to_dt(qs, date_time):
        greater = qs.filter(date_time__gte=date_time).order_by("date_time").first()
        less = qs.filter(date_time__lte=date_time).order_by("-date_time").first()

        if greater and less:
            return greater if abs(greater.date_time - date_time) < abs(less.date_time - date_time) else less
        else:
            return greater or less

    def get(self, request, *args, **kwargs):
        date_str = request.GET['date']
        date_str = date_str.replace(' ', '+')

        date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')

        closest_date = GetPosition.get_closest_to_dt(GpggaGpsFix.objects.all(), date)

        diff = closest_date.date_time - date
        if diff.seconds <= 360:
            position = {'latitude': closest_date.latitude,
                        'longitude': closest_date.longitude
                        }
        else:
            position = {'latitude': None, 'longitude': None}

        response = JsonResponse(status=200, data=position)
        return response


class FerryboxView(TemplateView):
    def get(self, request, *args, **kwargs):
        latest_information = Ferrybox.objects.latest()
        temperatures = get_ferrybox_data_24_hours('temperature')
        salinities = get_ferrybox_data_24_hours('salinity')
        fluorimeters = get_ferrybox_data_24_hours('fluorimeter')
        oxygen = get_ferrybox_data_24_hours('oxygen')

        now_utc = utils.set_utc(datetime.datetime.utcnow())

        latest_information_minutes_ago = int((now_utc - latest_information.date_time).seconds / 60)

        return render(request, "ferrybox.html", {"latest_information": latest_information,
                                                 "latest_information_minutes_ago": latest_information_minutes_ago,
                                                 "temperatures": json.dumps(temperatures),
                                                 "salinities": json.dumps(salinities),
                                                 "fluorimeter": json.dumps(fluorimeters),
                                                 "oxygen": json.dumps(oxygen)
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
        d['x'] = -((start_time - current_time).seconds / 3600)
        ferrybox = Ferrybox.objects.filter(Q(date_time__lte=current_time)).order_by('-date_time')

        if not ferrybox.exists():
            break

        ferrybox = model_to_dict(ferrybox[0])

        if field == 'oxygen' and ferrybox[field] == 0:
            # TODO: delete this if when there is more than 1 day of valid data
            break

        d['y'] = ferrybox[field]

        result.append(d)
        current_time -= delta_time

    return result
