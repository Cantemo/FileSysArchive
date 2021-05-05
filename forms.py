import os

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import FileSysArchiveConfig


class FileSysArchiveConfigForm(ModelForm):
    class Meta:
        model = FileSysArchiveConfig
        fields = ['storage_path']

    def clean_storage_path(self):
        storage_path = self.cleaned_data['storage_path']

        if os.path.isdir(storage_path):
            return storage_path
        else:
            raise forms.ValidationError(_("Invalid storage path, directory does not exists"))
