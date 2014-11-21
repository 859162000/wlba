# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Misc'
        db.create_table(u'misc_misc', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('stype', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('created_at', self.gf('django.db.models.fields.BigIntegerField')(default=1415859891L, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.BigIntegerField')(default=1415859891L, blank=True)),
        ))
        db.send_create_signal(u'misc', ['Misc'])


    def backwards(self, orm):
        # Deleting model 'Misc'
        db.delete_table(u'misc_misc')


    models = {
        u'misc.misc': {
            'Meta': {'object_name': 'Misc'},
            'created_at': ('django.db.models.fields.BigIntegerField', [], {'default': '1415859891L', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'stype': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.BigIntegerField', [], {'default': '1415859891L', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['misc']