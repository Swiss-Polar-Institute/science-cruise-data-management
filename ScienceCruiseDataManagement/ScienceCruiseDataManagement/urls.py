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

from main.views import MainMenuView, MainMapView, PositionsJson, LastShipPosition, CountryListView, FileStorageView, InteractiveMapView, EventListView, ImportPortsFromGpx, DocumentsView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', MainMenuView.as_view()),
    url(r'^map/$', MainMapView.as_view()),
    url(r'^api/positions.geojson', PositionsJson.as_view()),
    url(r'api/last_ship_position.json', LastShipPosition.as_view()),
    # url(r'^api/positions$', PositionsJson.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^country/list$', CountryListView.as_view(), name='article-list'),
    url(r'^storage/', FileStorageView.as_view()),
    url(r'^map/interactive/$', InteractiveMapView.as_view()),
    url(r'^reports/events/$', EventListView.as_view()),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^import_ports_from_gpx/', ImportPortsFromGpx.as_view()),
    url(r'^documents/', DocumentsView.as_view())
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static("/document_storage/", document_root=settings.DOCUMENTS_DIRECTORY) \
  + static("/ethz_forecast_data/", document_root=settings.FORECAST_DIRECTORY)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]