# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Account'
        db.create_table(u'weixin_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('classify', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('token', self.gf('django.db.models.fields.CharField')(default=u'BdstV5v4', max_length=32)),
            ('app_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('app_secret', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('access_token_content', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('access_token_expires_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('jsapi_ticket_content', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('jsapi_ticket_expires_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['Account'])


    def backwards(self, orm):
        # Deleting model 'Account'
        db.delete_table(u'weixin_account')


    models = {
        u'weixin.account': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Account'},
            'access_token_content': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'access_token_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'app_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'app_secret': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'classify': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jsapi_ticket_content': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'jsapi_ticket_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "u'YRlk0gKy'", 'max_length': '32'})
        }
    }

    complete_apps = ['weixin']