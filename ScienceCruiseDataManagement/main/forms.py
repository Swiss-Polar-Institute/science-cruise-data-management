from django import forms
from django.utils import timezone


class InputShipDateTime(forms.Form):
    ship_date_time = forms.DateTimeField(label='Date time of the ship (UTC) ')