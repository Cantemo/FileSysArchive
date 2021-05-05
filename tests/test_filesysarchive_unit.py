import mock

from portal.archive_framework.tests.plugins_checks_base import ArchivePluginBaseTests
from portal.plugins.filesysarchive.forms import FileSysArchiveConfigForm
from portal.plugins.filesysarchive.plugin import FileSysArchivePlugin
from portal.utils.decorators import memorized_method
from portal.utils.test_case import PortalLegacyTestCase


class FileSysArchivePluginTest(PortalLegacyTestCase, ArchivePluginBaseTests):

    @memorized_method()
    def get_plugin_instance(self):
        """
        Method that retrieves an initialized instance
        of an archive plugin
        """
        return FileSysArchivePlugin()

    def test_correct_configuration_view(self):
        """
        Test a valid plugin configuration Form
        request, checking that the response is
        expected.
        """
        data = {
            "storage_path": "/tmp",
        }
        form = FileSysArchiveConfigForm(data)

        with mock.patch("os.path.isdir", return_value=True) as mock_is_dir:
            self.assertTrue(form.is_valid())
            self.assertTrue(mock_is_dir.called)

    def test_incorrect_configuration_view(self):
        """
        Test an invalid plugin configuration Form
        request, checking that the response is
        expected.
        """
        data = {
            "storage_path": "/dasda/sfd/sdfdf",
        }
        form = FileSysArchiveConfigForm(data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors, {'storage_path': [u'Invalid storage path, directory does not exists']})

    def test_archive_single(self):
        """
        Test archive action for a single item
        """
        file_sets = self.get_filesets(qty=1)
        original_file_path = file_sets[0].files[0]

        # FileSysArchive plugin currently is doing nothing with the following parameters,
        # so tests should always pass if they are "None"
        policy = None
        job_id = None
        plugin = self.get_plugin_instance()

        with mock.patch("shutil.copy") as mocked_copy_file:
            archived, not_archived, error_string, extra_data = plugin.archive(file_sets, policy, job_id)
            self.assertEquals(mocked_copy_file.call_count, 1)

            call_arguments = mocked_copy_file.call_args[0]
            self.assertEquals(len(call_arguments), 2)

            self.assertEquals(
                call_arguments[0],
                original_file_path
            )

            self.assertEquals(
                call_arguments[1],
                u'/tmp/test_file_0_VX-0_b2c3235575f841d696d3e3c78d8e089f89508e45.txt'
            )

        self.assertEquals(error_string, '')
        self.assertEquals(not_archived, [])
        self.assertEquals(extra_data, {})

        self.assertEquals(
            self._set_filesets_external_ids(file_sets, replaced_filepath="/tmp"),
            archived
        )

    def test_archive_multiple_files(self):
        """
        Make sure that if we have multiple files for a fileset we only archive one of them.
        """
        file_sets = self.get_filesets(qty=1, files=2)
        original_file_path = file_sets[0].files[0]

        # FileSysArchive plugin currently is doing nothing with the following parameters,
        # so tests should always pass if they are "None"
        policy = None
        job_id = None
        plugin = self.get_plugin_instance()

        with mock.patch("shutil.copy") as mocked_copy_file:
            archived, not_archived, error_string, extra_data = plugin.archive(file_sets, policy, job_id)
            self.assertEquals(mocked_copy_file.call_count, 1)

            call_arguments = mocked_copy_file.call_args[0]
            self.assertEquals(len(call_arguments), 2)

            self.assertEquals(
                call_arguments[0],
                original_file_path
            )

            self.assertEquals(
                call_arguments[1],
                u'/tmp/test_file_0_VX-0_b2c3235575f841d696d3e3c78d8e089f89508e45.txt'
            )

        self.assertEquals(error_string, '')
        self.assertEquals(not_archived, [])
        self.assertEquals(extra_data, {})

        self.assertEquals(
            self._set_filesets_external_ids(file_sets, replaced_filepath="/tmp"),
            archived
        )

    def test_restore_single(self):
        """
        Test restore from archive action
        for a single item
        """
        file_sets = self.get_filesets(qty=1, external_ids=[["/tmp/random_path.jpg"]])
        original_file_path = file_sets[0].files[0]

        # FileSysArchive plugin currently is doing nothing with the following parameters,
        # so tests should always pass if they are "None"
        policy = None

        plugin = self.get_plugin_instance()
        with mock.patch("shutil.copy") as mocked_copy_file:
            plugin.restore(file_sets, policy)

            call_arguments = mocked_copy_file.call_args[0]
            self.assertEquals(len(call_arguments), 2)

            self.assertEquals(
                call_arguments[0],
                '/tmp/random_path.jpg'
            )

            self.assertEquals(
                call_arguments[1],
                original_file_path
            )

    def test_restore_more_files_than_external_ids(self):
        """
        Tests that we can successfully restore when a shape has multiple files
        Make sure we dont run into: https://vvv.cantemo.com/issues/20491
        """
        file_sets = self.get_filesets(qty=1, external_ids=[["/tmp/random_path.jpg"]], files=2)
        original_file_path = file_sets[0].files[0]

        # FileSysArchive plugin currently is doing nothing with the following parameters,
        # so tests should always pass if they are "None"
        policy = None

        plugin = self.get_plugin_instance()
        with mock.patch("shutil.copy") as mocked_copy_file:
            plugin.restore(file_sets, policy)

            call_arguments = mocked_copy_file.call_args[0]
            self.assertEquals(len(call_arguments), 2)

            self.assertEquals(
                call_arguments[0],
                '/tmp/random_path.jpg'
            )

            self.assertEquals(
                call_arguments[1],
                original_file_path
            )

    def test_delete_single(self):
        """
        Test delete from archive action
        for a single item
        """
        file_sets = self.get_filesets(qty=1, external_ids=[["/tmp/random_path.jpg"]])

        # FileSysArchive currently is doing nothing with the following parameters,
        # so tests should always pass if they are "None"
        policy = None
        plugin = self.get_plugin_instance()

        with mock.patch("os.unlink") as mocked_os_unlink:
            plugin.delete(file_sets, policy)

            self.assertEquals(mocked_os_unlink.call_count, 1)
            call_arguments = mocked_os_unlink.call_args[0]
            self.assertEquals(len(call_arguments), 1)

            self.assertEquals(
                call_arguments[0],
                "/tmp/random_path.jpg"
            )

    def test_archive_bulk(self):
        """
        Test archive action for a set of items
        """
        # this plugin does not support bulk operations
        # So just assert that it does not have bulk policies.
        # If bulk policies are created, then this test needs to be updated
        # to cover that.
        self.assertEquals(False, self.plugin_has_bulk_policy())

    def test_restore_bulk(self):
        """
        Test restore from archive action
        for a set of items
        """
        # this plugin does not support bulk operations
        # So just assert that it does not have bulk policies.
        # If bulk policies are created, then this test needs to be updated
        # to cover that.
        self.assertEquals(False, self.plugin_has_bulk_policy())
        self.assertFalse(hasattr(self.get_plugin_instance(), "restore_bulk"))

    def test_delete_bulk(self):
        """
        Test delete from archive action
        for a set of items
        """
        # this plugin does not support bulk operations
        # So just assert that it does not have bulk policies.
        # If bulk policies are created, then this test needs to be updated
        # to cover that.
        self.assertEquals(False, self.plugin_has_bulk_policy())
