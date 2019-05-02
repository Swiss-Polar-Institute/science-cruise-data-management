import astral

from django.shortcuts import render
from django.views.generic import TemplateView
from sunset_sunrise.forms import InputPositionDate

import datetime


class SunsetSunrise(TemplateView):
    def get(self, request, *args, **kwargs):
        form = InputPositionDate()
        return render(request, "sunset_sunrise.html", {"form": form})

    def post(self, request, *args, **kwargs):
        template_information = {}

        error_message = ""
        try:
            latitude = float(request.POST['latitude'])
            longitude = float(request.POST['longitude'])
        except ValueError:
            error_message += "Latitude and longitude need to be in decimal degrees. E.g. 78.42 or -10.24"

        try:
            date = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d").date()
        except ValueError:
            date = datetime.datetime.today()
            error_message += "Invalid date time. It needs to be YYYY-MM-DD"

        if error_message != "":
            form = InputPositionDate()
            return render(request, "sunset_sunrise.html", {'form': form,
                                                           'error_message': error_message})

        template_information['latitude'] = latitude
        template_information['longitude'] = longitude
        template_information['date'] = request.POST['date']

        place = astral.Location()
        place.latitude = latitude
        place.longitude = longitude

        template_information['sunrise'] = place.sunrise(date=date)
        template_information['dawn'] = place.dawn(date=date)
        template_information['dusk'] = place.dusk(date=date)
        template_information['sunset'] = place.sunset(date=date)
        template_information['date_parsed'] = date.strftime("%Y-%m-%d")

        template_information['error_message'] = error_message

        template_information['form'] = InputPositionDate(initial={'latitude': place.latitude,
                                                                  'longitude': place.longitude})

        return render(request, "sunset_sunrise_exec.html", template_information)

