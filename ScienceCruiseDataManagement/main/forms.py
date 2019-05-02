from django import forms
from django.utils import timezone

import datetime

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

class InputShipDateTime(forms.Form):
    ship_date_time = forms.DateTimeField(required=False,
                                         label='Date time of the ship (UTC)')

    ship_date_times = forms.CharField(help_text="""List of date times that could be copied from a spreadsheet and the results copied back<br>
                                                Must be in format YYYY-MM-DD HH:MM:SS.""",
                                      required=False,
                                      label='List of date times (UTC)',
                                      widget=forms.Textarea(attrs={'cols': "20", 'rows': "10", }))


class InputShipTimes(forms.Form):
    ship_date_times = forms.CharField(help_text="""List of date times that could be copied from a spreadsheet and the results copied back<br>
                                                Must be in format YYYY-MM-DD HH:MM:SS.""",
                                      required=True,
                                      label='List of date times (ship time)',
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

