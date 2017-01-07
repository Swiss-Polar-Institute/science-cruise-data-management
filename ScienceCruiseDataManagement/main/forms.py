from django import forms
from django.utils import timezone


class InputShipDateTime(forms.Form):
    ship_date_time = forms.DateTimeField(required=False, label='Date time of the ship (UTC) ')
    ship_date_times = forms.CharField(help_text="""List of date times that could be copied from a spreadsheet and the results copied back<br>
                                                Must be in format YYYY-MM-DD HH:MM:SS.""", required=False, label='List of date times (UTC)', widget=forms.Textarea(attrs={'cols': "20", 'rows': "10", }))
