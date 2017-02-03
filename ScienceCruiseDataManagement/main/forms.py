from django import forms
from django.utils import timezone


class InputShipDateTime(forms.Form):
    ship_date_time = forms.DateTimeField(required=False,
                                         label='Date time of the ship (UTC)')

    ship_date_times = forms.CharField(help_text="""List of date times that could be copied from a spreadsheet and the results copied back<br>
                                                Must be in format YYYY-MM-DD HH:MM:SS.""",
                                      required=False,
                                      label='List of date times (UTC)',
                                      widget=forms.Textarea(attrs={'cols': "20", 'rows': "10", }))


class InputCoordinates(forms.Form):
    coordinates = forms.CharField(help_text="""List of coordinates to convert. Must be in one of the formats:<br>
24 53 42.300 S 24 53 42.300 E<br>
24 53.705 S 24 53.705 W<br>
-24.895 24.895
<br>
""",
                                  required=True,
                                  label="List of coordinates",
                                  widget=forms.Textarea(attrs={"cols": "40", "rows": "20", }))
