"""ScienceCruiseDataManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from main.views import MainMenuView
from main.views import MainMapView
from main.views import EventsJson
from main.views import CountryListView
from main.views import StorageView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', MainMenuView.as_view()),
    url(r'^map/$', MainMapView.as_view()),
    url(r'^api/events.geojson', EventsJson.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^country/list$', CountryListView.as_view(), name='article-list'),
    url(r'^storage/', StorageView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]