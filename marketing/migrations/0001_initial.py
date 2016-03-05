# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Channels'
        db.create_table(u'marketing_channels', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=12, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100, blank=True)),
            ('coop_status', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=2)),
            ('merge_code', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('classification', self.gf('django.db.models.fields.CharField')(default='----', max_length=20)),
            ('platform', self.gf('django.db.models.fields.CharField')(default='full', max_length=20)),
            ('start_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_abandoned', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'marketing', ['Channels'])


    def backwards(self, orm):
        # Deleting model 'Channels'
        db.delete_table(u'marketing_channels')


    models = {
        u'marketing.channels': {
            'Meta': {'object_name': 'Channels'},
            'classification': ('django.db.models.fields.CharField', [], {'default': "'----'", 'max_length': '20'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'coop_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'is_abandoned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'merge_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "'full'", 'max_length': '20'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['marketing']