from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry

from .models import ChildDevice


class DeviceLookup(ModelLookup):
    model = ChildDevice
    search_fields = ('name__icontains', )

registry.register(DeviceLookup)