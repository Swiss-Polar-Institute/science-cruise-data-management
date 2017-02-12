from django.shortcuts import render
from django.views.generic import TemplateView
from ship_data.models import Ferrybox

class FerryboxView(TemplateView):
    def get(self, request, *args, **kwargs):
        latest_information = Ferrybox.objects.latest()
        return render(request, "ferrybox.html", {"latest_information": latest_information})


# Create your views here.
