# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table(u'file_storage_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('content', self.gf('django.db.models.fields.BinaryField')(max_length=20971520)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'file_storage', ['File'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table(u'file_storage_file')


    models = {
        u'file_storage.file': {
            'Meta': {'object_name': 'File'},
            'content': ('django.db.models.fields.BinaryField', [], {'max_length': '20971520'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['file_storage']