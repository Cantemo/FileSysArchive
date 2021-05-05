import os
import requests
import time

from django.conf import settings

from portal.plugins.filesysarchive.plugin import FileSysArchivePlugin
from portal.utils.test_case import PortalLegacyTestCase
from django.contrib.auth.models import User

from portal.vidispine.iitem import ItemHelper
from portal.archive_framework.tasks.archive import archive, populate_archive_jobs
from portal.archive_framework.tasks.restore import restore, populate_restore_jobs
from portal.archive_framework.models import AggregateArchiveJob, ArchiveJob
from portal.archive_framework.utils import get_components


PLUGIN_NAME = "Test archive plugin"
CONTENT = {'content': ['metadata', 'thumbnail', 'poster', 'uri', 'shape'],
           'include': ['type', 'extradata']}


def _get_test_file(filename):
    return open(os.path.join(os.path.dirname(os.path.realpath(__file__)), filename), "rb")


class TestFilesysarchive(PortalLegacyTestCase):
    """
    Perform integration tests on the archive framework.
    Vidispine and Portal must be running before launching this test suite.
    """

    def __init__(self, *args, **kwargs):
        super(TestFilesysarchive, self).__init__(*args, **kwargs)

        self.plugin = FileSysArchivePlugin()
        self.plugin_id = self.plugin.plugin_guid

    def _ingest_file_to_vds(self, url, filename, auth):
        with _get_test_file(filename) as data_file:
            r = requests.post(url, auth=auth, headers={"Accept": "application/json"},
                              data=data_file, stream=True)
        self.assertEqual(200, r.status_code)
        job_id = r.json()["jobId"]
        self.assertTrue(job_id)
        return job_id

    def _get_item_id_by_job(self, job_id, item_id_key, auth):
        url = "%s:%s/API/job/%s" % (settings.VIDISPINE_URL, settings.VIDISPINE_PORT, job_id)
        r = requests.get(url, auth=auth, headers={"Accept": "application/json"},
                         stream=True)
        self.assertEqual(200, r.status_code)
        for data in r.json().get("data", []):
            if data["key"] == "item":
                setattr(self, item_id_key, data['value'])

    def _check_vd_hash(self, item_id, auth):
        url = "%s:%s/API/item/%s?content=shape" % (
            settings.VIDISPINE_URL, settings.VIDISPINE_PORT, item_id
        )
        r = requests.get(url, auth=auth, headers={"Accept": "application/xml"})
        self.assertEqual(200, r.status_code)
        return "<hash>" in r.text

    def setUp(self):
        super(TestFilesysarchive, self).setUp()
        self.user, _created = User.objects.get_or_create(
            username=settings.VIDISPINE_USERNAME,
            defaults={
                'password': settings.VIDISPINE_PASSWORD,
                'email': "test@example.com"
            }
        )
        self.assertTrue(self.user)

        auth = (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)

        url = "%s:%s/API/import/raw" % (settings.VIDISPINE_URL, settings.VIDISPINE_PORT)
        jobId = self._ingest_file_to_vds(url, 'jpeg.jpg', auth)
        jobId2 = self._ingest_file_to_vds(url, 'jpeg.jpg', auth)
        jobId3 = self._ingest_file_to_vds(url, 'test.txt', auth)

        self.item_id = None
        self.item_id2 = None
        self.item_id3 = None

        items_created = {
            jobId: 'item_id',
            jobId2: 'item_id2',
            jobId3: 'item_id3',
        }
        while not all([getattr(self, key) for key in items_created.values()]):
            for job_id, item_id in items_created.items():
                if not getattr(self, item_id):
                    self._get_item_id_by_job(job_id, item_id, auth)
            time.sleep(1)

        hash_statuses = {
            self.item_id: False,
            self.item_id2: False,
            self.item_id3: False,
        }

        while not all(hash_statuses.values()):
            for item_id, hash_status in hash_statuses.items():
                if not hash_status:
                    hash_statuses[item_id] = self._check_vd_hash(item_id, auth)
            time.sleep(1)

        self.item_ids = [self.item_id, self.item_id2, self.item_id3]

    def test_single_archive_task(self):
        populate_archive_jobs(
            {'item_ids': [self.item_id], 'purge_from_online_storage': True}, self.user.id, self.plugin.plugin_guid,
            self.plugin.get_policies()[0]['uuid'], self.plugin.name,
            self.plugin.get_policies()[0]['uuid'], processed_items=None
        )

        agg_job = AggregateArchiveJob.objects.latest("id")
        self.assertEquals(agg_job.jobs.count(), 1)
        for job in agg_job.jobs.all():
            archive(job.id, self.plugin.plugin_guid, self.plugin.get_policies()[0]['uuid'])

        ith = ItemHelper(runas=self.user)
        item = ith.getItem(self.item_id, content=CONTENT)

        for shape in item.getShapes():
            first_component = get_components(shape)[0]
            self.assertEqual(
                "ARCHIVED",
                ith.getComponentMetadataValue(
                    item.getId(),
                    shape.getId(),
                    first_component['component_id'],
                    "portal_archive_status"
                )
            )
            self.assertEqual(
                1, ArchiveJob.objects.filter(
                    status=ArchiveJob.SUCCESS, component_id=first_component['component_id']).count()
            )

        item = ith.getItem(self.item_id, content=CONTENT)
        self.assertEqual("Archived", item.getArchiveStatus())

        # test restore
        populate_restore_jobs(
            {'item_ids': [self.item_id], 'purge_from_online_storage': False},
            self.user.id
        )

        self.assertEquals(agg_job.jobs.count(), 1)
        for job in agg_job.jobs.all():
            restore([job.id], self.plugin.plugin_guid, self.plugin.get_policies()[0]['uuid'])

        item = ith.getItem(self.item_id, content=CONTENT)
        for shape in item.getShapes():
            first_component = get_components(shape)[0]
            self.assertEqual(
                2,
                ArchiveJob.objects.filter(
                    status=ArchiveJob.SUCCESS, component_id=first_component['component_id']).count()
            )

        self.assertEqual(
            "Archived/Restored", item.getArchiveStatus()
        )

        ith.removeItem(item.getId())

    def test_multi_archive_task(self):
        """
        Test the archival of several items in one operation, where at least two items contain files
         with the same sha1sum, and at least one item contain a file with a unique sha1sum
        """
        ith = ItemHelper(runas=self.user)

        # test archive
        populate_archive_jobs(
            {'item_ids': self.item_ids, 'purge_from_online_storage': True}, self.user.id, self.plugin.plugin_guid,
            self.plugin.get_policies()[0]['uuid'], self.plugin.name,
            self.plugin.get_policies()[0]['uuid'], processed_items=None
        )

        agg_job = AggregateArchiveJob.objects.latest("id")
        self.assertEquals(agg_job.jobs.count(), 3)
        for job in agg_job.jobs.all():
            archive(job.id, self.plugin.plugin_guid, self.plugin.get_policies()[0]['uuid'])

        for item in ith.getItems(self.item_ids, content=CONTENT):
            for shape in item.getShapes():
                first_component = get_components(shape)[0]
                status = ith.getComponentMetadataValue(
                    item.getId(),
                    shape.getId(),
                    first_component['component_id'],
                    "portal_archive_status"
                )
                self.assertEqual("ARCHIVED", status)
                self.assertEqual(
                    1, ArchiveJob.objects.filter(
                        status=ArchiveJob.SUCCESS, component_id=first_component['component_id']).count()
                )

        items = ith.getItems(self.item_ids, content=CONTENT)
        self.assertTrue(
            all([item.getArchiveStatus() == 'Archived'
                 for item in items])
        )

        # test restore
        populate_restore_jobs(
            {'item_ids': self.item_ids, 'purge_from_online_storage': False},
            self.user.id
        )

        agg_job = AggregateArchiveJob.objects.latest('id')
        self.assertEquals(agg_job.jobs.count(), 3)

        for job in agg_job.jobs.all():
            restore([job.id], self.plugin.plugin_guid, self.plugin.get_policies()[0]['uuid'])

        items = ith.getItems(self.item_ids, content=CONTENT)
        for item in ith.getItems(self.item_ids, content=CONTENT):
            for shape in item.getShapes():
                first_component = get_components(shape)[0]
                self.assertEqual(
                    2, ArchiveJob.objects.filter(
                        status=ArchiveJob.SUCCESS, component_id=first_component['component_id']).count()
                )

        self.assertTrue(
            all([item.getArchiveStatus() == 'Archived/Restored'
                 for item in items])
        )

        for item_id in self.item_ids:
            ith.removeItem(item_id)
