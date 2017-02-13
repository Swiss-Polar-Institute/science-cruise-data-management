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
from data_storage_management.views import HardDiskJson
from main.views import MainMenuView, MainMapView, PositionsJson, LatestShipPosition, CountryListView, FileStorageView,\
    InteractiveMapView, EventListView, ImportPortsFromGpx, DocumentsView, AccessingDataView, PositionFromDateTime,\
    CoordinatesConversion, TrackJson, MailState
from metadata.views import ProjectListView, MetadataEntryListView, MetadataEntryView
from ship_data.views import FerryboxView
from data_storage_management.views import HardDiskJson, DirectoryUpdateJson
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', MainMenuView.as_view()),
    url(r'^map/$', MainMapView.as_view()),
    url(r'^api/positions.geojson', PositionsJson.as_view()),
    url(r'^api/track.geojson', TrackJson.as_view()),
    url(r'api/latest_ship_position.json', LatestShipPosition.as_view()),
    url(r'api/data_storage/hard_disk.json', HardDiskJson.as_view()),
    url(r'api/data_storage/add_directory_update.json', DirectoryUpdateJson.as_view()),
    # url(r'^api/positions$', PositionsJson.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^country/list$', CountryListView.as_view(), name='article-list'),
    url(r'^storage/', FileStorageView.as_view()),
    url(r'^map/interactive/$', InteractiveMapView.as_view()),
    url(r'^reports/events/$', EventListView.as_view()),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^import_ports_from_gpx/', ImportPortsFromGpx.as_view()),
    url(r'^documents/', DocumentsView.as_view()),
    url(r'^accessing_data/', AccessingDataView.as_view()),
    url(r'^position_from_date_time/', PositionFromDateTime.as_view()),
    url(r'^coordinates_conversion/', CoordinatesConversion.as_view()),
    url(r'^mail_state/', MailState.as_view()),
    url(r'^ferrybox/', FerryboxView.as_view()),
    url(r'^metadata/$', MetadataEntryListView.as_view()),
    url(r'^metadata/([0-9])+/$', MetadataEntryView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static("/documents_storage/", document_root=settings.DOCUMENTS_DIRECTORY) \
  + static("/ethz_forecast_data/", document_root=settings.FORECAST_DIRECTORY)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]