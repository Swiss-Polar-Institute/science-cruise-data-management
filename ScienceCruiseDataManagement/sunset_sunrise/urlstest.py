from django.conf.urls import url
from sunset_sunrise.views import SunsetSunrise

urlpatterns = [
    url(r'^sunset_sunrise/', SunsetSunrise.as_view())
]
