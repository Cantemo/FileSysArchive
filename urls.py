
from django.conf.urls.defaults import patterns, url
from .views import FileSysArchiveSettings

urlpatterns = patterns('portal.plugins.filesysarchive.views',
    url(r'^filesysarchive/settings/$',
        FileSysArchiveSettings.as_view(),
        name='filesysarchive_settings'),
)
