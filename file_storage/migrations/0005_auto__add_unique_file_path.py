# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'File', fields ['path']
        db.create_unique(u'file_storage_file', ['path'])


    def backwards(self, orm):
        # Removing unique constraint on 'File', fields ['path']
        db.delete_unique(u'file_storage_file', ['path'])


    models = {
        u'file_storage.file': {
            'Meta': {'object_name': 'File'},
            'content': ('django.db.models.fields.BinaryField', [], {'max_length': '20971520'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['file_storage']