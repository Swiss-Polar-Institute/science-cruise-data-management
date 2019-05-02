from django import forms
import datetime

class InputPositionDate(forms.Form):
    latitude = forms.CharField(help_text="Latitude where the sunset/sunrise is going to be calculated",
                               required=True,
                               label="Latitude")

    longitude = forms.CharField(help_text="Longitude where the sunset/sunrise is going to be calculated",
                                required=True,
                                label="Longitude")

    date = forms.DateField(initial=datetime.date.today,
                           help_text="Empty if it's for today",
                           required=False,
                           label="Date")
