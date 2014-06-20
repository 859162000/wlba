# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IdVerification'
        db.create_table(u'wanglibao_account_idverification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_number', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_account', ['IdVerification'])


    def backwards(self, orm):
        # Deleting model 'IdVerification'
        db.delete_table(u'wanglibao_account_idverification')


    models = {
        u'wanglibao_account.idverification': {
            'Meta': {'object_name': 'IdVerification'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['wanglibao_account']