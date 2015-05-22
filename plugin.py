import logging
import os
import shutil

from slugify import slugify

from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IAppRegister
from portal.generic.plugin_interfaces import IArchivePlugin
from portal.generic.plugin_interfaces import IPluginBlock
from portal.generic.plugin_interfaces import IPluginURL
from portal.archive_framework.utils import construct_filename

log = logging.getLogger(__name__)
PLUGIN_NAME = "Simple archive plugin"


class FileSysArchiveUrls(Plugin):
    implements(IPluginURL)

    def __init__(self):
        self.name = "Acts on FileSysArchive URLs for Item"
        self.urls = 'portal.plugins.filesysarchive.urls'
        self.urlpattern = ''
        self.namespace = 'filesysarchive'
        log.debug("Initiated FileSysArchiveUrls")

FileSysArchiveUrls()


class FileSysArchivePlugin(Plugin):
    """
    Simple archive plugin that stores the file to archive in file system (Default: /tmp)
    """
    implements(IArchivePlugin)
    plugin_guid = "73d12cff-6405-4e4b-9944-308c7add5d79"

    def __init__(self):
        self.plugin_guid = FileSysArchivePlugin.plugin_guid
        self.name = PLUGIN_NAME
        log.info(self.name + " initialized")

    @staticmethod
    def archive(file_sets):
        from .models import get_config
        config = get_config()
        archived = []

        for file_set in file_sets:
            for file_path in file_set.files:
                shutil.copy(
                    file_path, construct_filename(file_path, file_set, config.storage_path)
                )
            archived.append(file_set)

        return archived

    @staticmethod
    def restore(file_sets):
        from .models import get_config
        config = get_config()
        restored = []
        for file_set in file_sets:
            for dst_path in file_set.files:
                try:
                    dir_name = os.path.dirname(dst_path)
                    if dir_name and (not os.path.exists(dir_name)):
                        os.makedirs(dir_name)
                    shutil.copy(
                        construct_filename(dst_path, file_set, config.storage_path), dst_path
                    )
                    restored.append(file_set)
                    break
                except Exception as x:
                    log.error(x, exc_info=True)
                    raise x
        return restored

    @staticmethod
    def delete(file_sets):
        from .models import get_config
        config = get_config()
        for file_set in file_sets:
            for file_path in file_set.files:
                try:
                    os.unlink(construct_filename(file_path, file_set, config.storage_path))
                except Exception as x:
                    log.error(x, exc_info=True)
                    raise x
        return file_sets

    @staticmethod
    def is_ready():
        return True


class FileSysArchiveAppRegister(Plugin):
    implements(IAppRegister)

    plugin_guid = "5e92dac9-e8e1-4a01-a654-acefa6286dd8"

    def __init__(self):
        file_sys_archive_plugin = FileSysArchivePlugin()
        self.name = file_sys_archive_plugin.name
        self.plugin_guid = FileSysArchiveAppRegister.plugin_guid

    def __call__(self):
        return {
            'name': self.name,
            'version': '1.0.0',
            'author': 'Cantemo AB',
            'author_url': 'www.cantemo.com',
            'notes': 'Copyright (C) 2015. All rights reserved.'}


FileSysArchiveAppRegister()


class FileSysArchiveAdminPlugin(Plugin):

    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = "69BAE5B4-EEE7-4845-A2C7-72866867FB9B"

    def return_string(self, tagname, *args):
        return {
            'guid': self.plugin_guid,
            'template': 'file_sys_archive/navigation_admin.html'
        }

FileSysArchiveAdminPlugin()


class FileSysArchiveAdminMenu(Plugin):
    """ adds a menu item to the admin screen
    """
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = "92D4597B-2015-4953-A980-183AE19B501A"

    def return_string(self, tagname, *args):
        return {
            'guid': self.plugin_guid,
            'template': 'file_sys_archive/admin_leftpanel_settings.html'
        }

FileSysArchiveAdminMenu()
