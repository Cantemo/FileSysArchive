import logging

from django.urls import reverse
from django.http import HttpResponseRedirect

from rest_framework.response import Response

from portal.generic.baseviews import CView
from portal.generic.decorators import HasAnyRole
from portal.themes.renderers import ThemeTemplateHTMLRenderer
from .forms import FileSysArchiveConfigForm
from .models import get_config

log = logging.getLogger(__name__)


class FileSysArchiveSettings(CView):

    template_name = 'file_sys_archive_example/settings.html'
    roles = ['portal_archive_settings']
    permission_classes = (HasAnyRole,)

    renderer_classes = (ThemeTemplateHTMLRenderer,)

    @staticmethod
    def _get_form(data=None):
        return FileSysArchiveConfigForm(data, instance=get_config())

    def get(self, request):
        return Response({'form': self._get_form()})

    def post(self, request):
        form = self._get_form(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse("filesysarchive_example_settings"))

        return Response({'form': form})
