import logging
import os
import errno
import shutil

from portal.archive_framework.utils import construct_filename, get_paths_to_restore_or_delete_from_external_ids
from portal.generic.plugin_interfaces import IPluginBlock
from portal.generic.plugin_interfaces import IPluginURL
from portal.pluginbase.core import Plugin, implements, ArchivePlugin

log = logging.getLogger(__name__)
PLUGIN_NAME = "File System Archive Example"


class FileSysArchiveUrls(Plugin):
    implements(IPluginURL)

    def __init__(self):
        self.name = "Acts on FileSysArchive URLs for Item"
        self.urls = 'portal.plugins.filesysarchive_example.urls'
        self.urlpattern = ''
        self.namespace = 'filesysarchive_example'
        log.debug("Initiated FileSysArchiveUrls")


FileSysArchiveUrls()


class FileSysArchivePlugin(ArchivePlugin):
    """
    Simple archive plugin that stores the file to archive in file system (Default: /tmp)
    """
    plugin_guid = "41E00013-517F-4D7C-AAC3-66EE75A203AE"

    def __init__(self):
        self.plugin_guid = FileSysArchivePlugin.plugin_guid
        self.name = PLUGIN_NAME
        self.role_archive = 'portal_archive_filesys'
        self.role_restore = 'portal_restore_filesys'
        self.role_purge = 'portal_purge_filesys'
        self.role_delete = 'portal_delete_filesys'
        log.info(self.name + " initialized")

    @staticmethod
    def archive(file_sets, policy_uuid, job_id):
        from .models import get_config
        config = get_config()

        archived = []
        not_archived = []

        log.debug("FileSysArchivePlugin, archive(), config.storage_path: %r", config.storage_path)
        # file_sets is a list of FileSet objects in the bulk archive case, which this plugin
        # does not support. Handle each separately.
        for file_set in file_sets:
            external_ids = []
            try:
                # FileSet has a list of files - since the shape can be on multiple storage - we
                # try to simply copy from the first here. A better logic would be be able to ignore
                # files that are not accessible - it's enough to find one we can read.
                for file_index, absolute_filename in enumerate(file_set.files):
                    archive_destination_path = construct_filename(absolute_filename, file_set, config.storage_path)

                    log.debug(
                        "FileSysArchivePlugin, archive(), Copying file from %s to %s"
                        % (absolute_filename, archive_destination_path)
                    )

                    shutil.copy(absolute_filename, archive_destination_path)
                    external_ids.append(archive_destination_path)
                    break

                # We set the path to external_ids on the FileSet, this gets stored on the item
                # and is available on restore()
                file_set = file_set._replace(external_ids=external_ids)

                archived.append(file_set)
            except IOError:
                not_archived.append(file_set)

        log.debug("FileSysArchivePlugin, archive done: %s", archived)
        if not_archived:
            log.error("FileSysArchivePlugin, the following file failed: %s", not_archived)
            error_string = "Could not copy file to archive"
        else:
            error_string = ""

        return archived, not_archived, error_string, {}

    @staticmethod
    def _get_paths_to_restore_or_delete(file_set):
        """
        Given a fileset, retrieves a list of tuples which each tuple has the following format:
            (archived file path, local path to copy the archived file to)

        So this retrieves the paths for doing the copy/delete operations.
        """
        return get_paths_to_restore_or_delete_from_external_ids(file_set)

    @staticmethod
    def restore(file_sets, policy_uuid):
        restored = []
        for file_set in file_sets:
            for archived_file_path, dst_path in FileSysArchivePlugin._get_paths_to_restore_or_delete(file_set):
                dir_name = os.path.dirname(dst_path)
                try:
                    os.makedirs(dir_name)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        log.error("Failed to create folder %s! Error was: %s" % (dir_name, e))
                        continue
                try:
                    shutil.copy(archived_file_path, dst_path)
                    restored.append(file_set)
                except Exception as x:
                    log.error(x, exc_info=True)
                    raise x
        return restored

    @staticmethod
    def delete(file_sets, policy_uuid):
        for file_set in file_sets:
            for archived_file_path, storage_path in FileSysArchivePlugin._get_paths_to_restore_or_delete(file_set):
                os.unlink(archived_file_path)

    @staticmethod
    def get_policies():
        return [
            {
                'uuid': "filesys_example",
                'bulk_support': False,
            }
        ]

    def is_ready(self):
        return True


FileSysArchivePlugin()


class FileSysArchiveAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self._log_about_deprecation = False
        self.name = "NavigationArchivePlugin"
        self.plugin_guid = "A56E3B15-9794-481B-A5AF-0A355325EA2A"

    def return_string(self, tagname, *args):
        return {
            'guid': self.plugin_guid,
            'template': 'file_sys_archive_example/navigation_admin.html'
        }


FileSysArchiveAdminPlugin()


class FileSysArchiveAdminMenu(Plugin):
    """ adds a menu item to the admin screen
    """
    implements(IPluginBlock)

    def __init__(self):
        self._log_about_deprecation = False
        self.name = "admin_left_panel_inside_archive"
        self.plugin_guid = "B85C1D2A-68BF-4BFA-BFD6-8818237744A5"

    def return_string(self, *_):
        return {
            'guid': self.plugin_guid,
            'template': 'file_sys_archive_example/admin_leftpanel_settings.html'
        }


FileSysArchiveAdminMenu()
