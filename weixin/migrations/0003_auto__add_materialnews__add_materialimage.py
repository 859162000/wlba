# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MaterialNews'
        db.create_table(u'weixin_materialnews', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('media_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('update_time', self.gf('django.db.models.fields.IntegerField')()),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['weixin.Account'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['MaterialNews'])

        # Adding model 'MaterialImage'
        db.create_table(u'weixin_materialimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('media_id', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('update_time', self.gf('django.db.models.fields.IntegerField')()),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['weixin.Account'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['MaterialImage'])


    def backwards(self, orm):
        # Deleting model 'MaterialNews'
        db.delete_table(u'weixin_materialnews')

        # Deleting model 'MaterialImage'
        db.delete_table(u'weixin_materialimage')


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
            'token': ('django.db.models.fields.CharField', [], {'default': "u'DN48hqGE'", 'max_length': '32'})
        },
        u'weixin.material': {
            'Meta': {'object_name': 'Material'},
            'account': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['weixin.Account']", 'unique': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'news_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'video_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'voice_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'weixin.materialimage': {
            'Meta': {'object_name': 'MaterialImage'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.Account']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'update_time': ('django.db.models.fields.IntegerField', [], {})
        },
        u'weixin.materialnews': {
            'Meta': {'object_name': 'MaterialNews'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.Account']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'update_time': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['weixin']