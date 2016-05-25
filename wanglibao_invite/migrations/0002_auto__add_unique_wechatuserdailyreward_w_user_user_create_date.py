# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'WechatUserDailyReward', fields ['w_user', 'user', 'create_date']
        db.create_unique(u'wanglibao_invite_wechatuserdailyreward', ['w_user_id', 'user_id', 'create_date'])


    def backwards(self, orm):
        # Removing unique constraint on 'WechatUserDailyReward', fields ['w_user', 'user', 'create_date']
        db.delete_unique(u'wanglibao_invite_wechatuserdailyreward', ['w_user_id', 'user_id', 'create_date'])


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
        u'wanglibao_invite.inviterelation': {
            'Meta': {'unique_together': "(('user', 'inviter'),)", 'object_name': 'InviteRelation'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inviter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inviter'", 'to': u"orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invited'", 'to': u"orm['auth.User']"})
        },
        u'wanglibao_invite.userextrainfo': {
            'Meta': {'object_name': 'UserExtraInfo'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_experience_amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'wanglibao_invite.wechatuserdailyreward': {
            'Meta': {'ordering': "('-create_date',)", 'unique_together': "(('w_user', 'create_date'), ('w_user', 'user', 'create_date'))", 'object_name': 'WechatUserDailyReward'},
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'experience_gold_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'experience_gold_record_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redpack_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'redpack_record_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'reward_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'w_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['weixin.WeixinUser']"})
        },
        u'weixin.authorizeinfo': {
            'Meta': {'object_name': 'AuthorizeInfo'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'access_token_expires_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
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
            'openid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'scene_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unbind_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unionid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'unsubscribe_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        }
    }

    complete_apps = ['wanglibao_invite']