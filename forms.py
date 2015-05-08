import os
import errno

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import FileSysArchiveConfig


class FileSysArchiveConfigForm(ModelForm):
    class Meta:
        model = FileSysArchiveConfig

    def clean_storage_path(self):
        storage_path = self.cleaned_data['storage_path']

        try:
            os.makedirs(storage_path)
        except OSError as exc:
            if not (exc.errno == errno.EEXIST or os.path.isdir(storage_path)):
                raise forms.ValidationError(_("Can't create directory"))

        return storage_path
