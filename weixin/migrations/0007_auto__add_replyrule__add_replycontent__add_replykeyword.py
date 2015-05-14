# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReplyRule'
        db.create_table(u'weixin_replyrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('pattern', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['weixin.Account'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['ReplyRule'])

        # Adding M2M table for field replies on 'ReplyRule'
        m2m_table_name = db.shorten_name(u'weixin_replyrule_replies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('replyrule', models.ForeignKey(orm[u'weixin.replyrule'], null=False)),
            ('replycontent', models.ForeignKey(orm[u'weixin.replycontent'], null=False))
        ))
        db.create_unique(m2m_table_name, ['replyrule_id', 'replycontent_id'])

        # Adding model 'ReplyContent'
        db.create_table(u'weixin_replycontent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('classify', self.gf('django.db.models.fields.CharField')(default='text', max_length=10)),
            ('media_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['ReplyContent'])

        # Adding model 'ReplyKeyword'
        db.create_table(u'weixin_replykeyword', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('pattern', self.gf('django.db.models.fields.IntegerField')()),
            ('rule_reply', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['weixin.ReplyRule'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'weixin', ['ReplyKeyword'])


    def backwards(self, orm):
        # Deleting model 'ReplyRule'
        db.delete_table(u'weixin_replyrule')

        # Removing M2M table for field replies on 'ReplyRule'
        db.delete_table(db.shorten_name(u'weixin_replyrule_replies'))

        # Deleting model 'ReplyContent'
        db.delete_table(u'weixin_replycontent')

        # Deleting model 'ReplyKeyword'
        db.delete_table(u'weixin_replykeyword')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'weixin.account': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Account'},
            'access_token_content': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'access_token_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'app_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'app_secret': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'classify': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jsapi_ticket_content': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'jsapi_ticket_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'oauth_access_token_content': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'oauth_access_token_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'oauth_refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'original_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "u'56mh8XGv'", 'max_length': '32'})
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
        },
        u'weixin.replycontent': {
            'Meta': {'object_name': 'ReplyContent'},
            'classify': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '10'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_id': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'weixin.replykeyword': {
            'Meta': {'object_name': 'ReplyKeyword'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.IntegerField', [], {}),
            'rule_reply': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.ReplyRule']"})
        },
        u'weixin.replyrule': {
            'Meta': {'object_name': 'ReplyRule'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.Account']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'pattern': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'replies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['weixin.ReplyContent']", 'symmetrical': 'False'})
        },
        u'weixin.weixinuser': {
            'Meta': {'object_name': 'WeixinUser'},
            'account_original_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'headimgurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'openid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        }
    }

    complete_apps = ['weixin']