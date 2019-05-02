from django import template
from django.utils.safestring import mark_safe

import main.utils as utils

register = template.Library()


def to_ship_timezone(date):
    return mark_safe('<font color="blue">' + utils.format_date_time(utils.date_utc_to_ship_time(date)) + "</font>")


register.filter('to_ship_timezone', to_ship_timezone)