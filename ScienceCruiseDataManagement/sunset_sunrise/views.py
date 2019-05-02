import astral

from django.shortcuts import render
from django.views.generic import TemplateView
from sunset_sunrise.forms import InputPositionDate
import main.utils as utils

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

        template_information['sunrise_utc'] = place.sunrise(date=date)
        template_information['dawn_utc'] = place.dawn(date=date)
        template_information['dusk_utc'] = place.dusk(date=date)
        template_information['sunset_utc'] = place.sunset(date=date)
        template_information['date_parsed'] = date.strftime("%Y-%m-%d")

        template_information['sunrise_ship_time'] = utils.format_date_time(utils.date_utc_to_ship_time(place.sunrise(date=date)))
        template_information['dawn_ship_time'] = utils.format_date_time(utils.date_utc_to_ship_time(place.dawn(date=date)))
        template_information['dusk_ship_time'] = utils.format_date_time(utils.date_utc_to_ship_time(place.dusk(date=date)))
        template_information['sunset_ship_time'] = utils.format_date_time(utils.date_utc_to_ship_time(place.sunset(date=date)))
        template_information['date_parsed'] = date.strftime("%Y-%m-%d")

        template_information['error_message'] = error_message

        template_information['form'] = InputPositionDate(initial={'latitude': place.latitude,
                                                                  'longitude': place.longitude})

        return render(request, "sunset_sunrise_exec.html", template_information)

