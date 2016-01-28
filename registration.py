import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IAppRegister, IPluginBootstrap

from portal.utils.apps import is_app_enabled

log = logging.getLogger(__name__)

app_id = 'com.cantemo.portal.filesysarchive'


class FileSysArchiveAppRegister(Plugin):
    implements(IAppRegister)

    def __init__(self):
        self.name = "filesysarchive"
        self.plugin_guid = "5e92dac9-e8e1-4a01-a654-acefa6286dd8"

    def __call__(self):
        from __init__ import __version__
        return {
            'name': "Filesystem Archive",
            'version': __version__,
            'author': 'Cantemo AB',
            'author_url': 'www.cantemo.com',
            'notes': 'Copyright (C) 2015. All rights reserved.',
            'enabled': is_app_enabled(app_id),
            'app_id': app_id
        }

FileSysArchiveAppRegister()


class FileSysArchiveBootstrap(Plugin):

    implements(IPluginBootstrap)

    def bootstrap(self):
        if is_app_enabled(app_id):
            import plugin

FileSysArchiveBootstrap()
