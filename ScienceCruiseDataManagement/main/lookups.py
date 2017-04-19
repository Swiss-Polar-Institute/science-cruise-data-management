from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry

from .models import DeviceType

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

class DeviceTypeLookup(ModelLookup):
    model = DeviceType
    search_fields = ('name__icontains', )

registry.register(DeviceTypeLookup)