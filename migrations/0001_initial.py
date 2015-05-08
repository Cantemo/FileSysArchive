# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileSysArchiveConfig'
        db.create_table('filesysarchive_filesysarchiveconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('storage_path', self.gf('django.db.models.fields.CharField')(default='/tmp/', max_length=255)),
        ))
        db.send_create_signal('filesysarchive', ['FileSysArchiveConfig'])

    def backwards(self, orm):
        # Deleting model 'FileSysArchiveConfig'
        db.delete_table('filesysarchive_filesysarchiveconfig')

    models = {
        'filesysarchive.filesysarchiveconfig': {
            'Meta': {'object_name': 'FileSysArchiveConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'storage_path': ('django.db.models.fields.CharField', [], {'default': "'/tmp/'", 'max_length': '255'})
        }
    }

    complete_apps = ['filesysarchive']