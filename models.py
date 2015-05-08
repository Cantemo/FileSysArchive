
from django.db import models
from django.utils.translation import ugettext_lazy as _

from portal.utils.models import SingletonModel


class FileSysArchiveConfig(SingletonModel):
    """Configuration model for FileSysArchive

    This holds the configuration information.
    """

    storage_path = models.CharField(
        _('Storage path'),
        max_length=255,
        blank=False,
        null=False,
        default='/tmp/',
        help_text=_("System will automatically create directory if it's possible")
    )


def get_config():
    try:
        return FileSysArchiveConfig.objects.get()
    except FileSysArchiveConfig.DoesNotExist:
        return FileSysArchiveConfig.objects.create()
