
from django.conf.urls import url
from .views import FileSysArchiveSettings

urlpatterns = [
    url(r'^filesysarchive_example/settings/$',
        FileSysArchiveSettings.as_view(),
        name='filesysarchive_example_settings'),
]
