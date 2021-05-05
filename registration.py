import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IAppRegister, IPluginBootstrap

from portal.utils.apps import is_app_enabled

log = logging.getLogger(__name__)

app_id = 'com.cantemo.portal.filesysarchive_example'


class FileSysArchiveAppRegister(Plugin):
    implements(IAppRegister)

    def __init__(self):
        self.name = "FileSysArchive Example"
        self.plugin_guid = "F137BBBE-E64D-4A31-B1F8-9DD9037A3E50"

    def __call__(self):
        from .__init__ import __version__
        return {
            'name': self.name,
            'version': __version__,
            'author': 'Cantemo AB',
            'author_url': 'www.cantemo.com',
            'notes': 'Copyright © 2015-2021. All rights reserved.',
            'enabled': is_app_enabled(app_id),
            'app_id': app_id
        }


FileSysArchiveAppRegister()


class FileSysArchiveBootstrap(Plugin):

    implements(IPluginBootstrap)

    def bootstrap(self):
        if is_app_enabled(app_id):
            from . import plugin


FileSysArchiveBootstrap()
