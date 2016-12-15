from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry

from .models import DeviceType


class DeviceTypeLookup(ModelLookup):
    model = DeviceType
    search_fields = ('name__icontains', )

registry.register(DeviceTypeLookup)