# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SceneRecord'
        db.create_table(u'weixin_scenerecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('openid', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('scene_str', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'weixin', ['SceneRecord'])


    def backwards(self, orm):
        # Deleting model 'SceneRecord'
        db.delete_table(u'weixin_scenerecord')


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
            'Meta': {'ordering': "[u'-created_at']", 'object_name': 'Account'},
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
            'token': ('django.db.models.fields.CharField', [], {'default': "u'kD4qXLHQ'", 'max_length': '32'})
        },
        u'weixin.authorizeinfo': {
            'Meta': {'object_name': 'AuthorizeInfo'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'access_token_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
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
        u'weixin.qrcode': {
            'Meta': {'ordering': "[u'-account_original_id', u'-create_at']", 'object_name': 'QrCode'},
            'account_original_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'expire_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'qrcode_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'ticket': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'weiXinChannel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.WeiXinChannel']", 'null': 'True'})
        },
        u'weixin.replycontent': {
            'Meta': {'object_name': 'ReplyContent'},
            'classify': ('django.db.models.fields.CharField', [], {'default': "u'text'", 'max_length': '10'}),
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
        u'weixin.scenerecord': {
            'Meta': {'object_name': 'SceneRecord'},
            'create_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'openid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'scene_str': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'weixin.subscriberecord': {
            'Meta': {'object_name': 'SubscribeRecord'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.SubscribeService']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unsubscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'w_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.WeixinUser']", 'null': 'True'})
        },
        u'weixin.subscribeservice': {
            'Meta': {'ordering': "[u'key']", 'object_name': 'SubscribeService'},
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'describe': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'num_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'weixin.weixinchannel': {
            'Meta': {'object_name': 'WeiXinChannel'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'digital_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_abandoned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '20'})
        },
        u'weixin.weixinuser': {
            'Meta': {'object_name': 'WeixinUser'},
            'account_original_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'auth_info': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.AuthorizeInfo']", 'null': 'True'}),
            'bind_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'headimgurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'openid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'scene_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unbind_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unionid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'unsubscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'weixin.weixinuseractionrecord': {
            'Meta': {'object_name': 'WeiXinUserActionRecord'},
            'action_describe': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'create_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'extra_data': ('wanglibao.fields.JSONFieldUtf8', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'w_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.WeixinUser']", 'null': 'True'})
        }
    }

    complete_apps = ['weixin']