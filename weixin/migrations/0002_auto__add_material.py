# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Material'
        db.create_table(u'weixin_material', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voice_count', self.gf('django.db.models.fields.IntegerField')()),
            ('video_count', self.gf('django.db.models.fields.IntegerField')()),
            ('image_count', self.gf('django.db.models.fields.IntegerField')()),
            ('news_count', self.gf('django.db.models.fields.IntegerField')()),
            ('expires_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('account', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['weixin.Account'], unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['Material'])


    def backwards(self, orm):
        # Deleting model 'Material'
        db.delete_table(u'weixin_material')


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
            'token': ('django.db.models.fields.CharField', [], {'default': "u'psRSByzD'", 'max_length': '32'})
        },
        u'weixin.material': {
            'Meta': {'object_name': 'Material'},
            'account': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['weixin.Account']", 'unique': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_count': ('django.db.models.fields.IntegerField', [], {}),
            'news_count': ('django.db.models.fields.IntegerField', [], {}),
            'video_count': ('django.db.models.fields.IntegerField', [], {}),
            'voice_count': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['weixin']