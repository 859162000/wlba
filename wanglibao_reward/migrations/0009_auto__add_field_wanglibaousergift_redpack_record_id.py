# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WanglibaoUserGift.redpack_record_id'
        db.add_column(u'wanglibao_reward_wanglibaousergift', 'redpack_record_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WanglibaoUserGift.redpack_record_id'
        db.delete_column(u'wanglibao_reward_wanglibaousergift', 'redpack_record_id')


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
        u'marketing.reward': {
            'Meta': {'ordering': "['-create_time']", 'object_name': 'Reward'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'wanglibao_activity.activity': {
            'Meta': {'ordering': "['-priority']", 'object_name': 'Activity'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'default': "u'\\u7ad9\\u5185\\u6d3b\\u52a8'", 'max_length': '20'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_all_channel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_stopped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "u'\\u5168\\u5e73\\u53f0'", 'max_length': '20'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'product_cats': ('django.db.models.fields.CharField', [], {'default': "u'P2P\\u4ea7\\u54c1'", 'max_length': '20'}),
            'product_ids': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'stopped_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'wanglibao_p2p.producttype': {
            'Meta': {'object_name': 'ProductType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_redpack.redpackevent': {
            'Meta': {'object_name': 'RedPackEvent'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x85\\xa8\\xe5\\xb9\\xb3\\xe5\\x8f\\xb0'", 'max_length': '10'}),
            'auto_extension': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_extension_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'available_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'describe': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'give_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'give_mode': ('django.db.models.fields.CharField', [], {'default': "u'\\u6ce8\\u518c'", 'max_length': '20', 'db_index': 'True'}),
            'give_platform': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x85\\xa8\\xe5\\xb9\\xb3\\xe5\\x8f\\xb0'", 'max_length': '10'}),
            'give_start_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'highest_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invest_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'p2p_types': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_p2p.ProductType']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '200', 'blank': 'True'}),
            'period_type': ('django.db.models.fields.CharField', [], {'default': "'month'", 'max_length': '20', 'blank': 'True'}),
            'rtype': ('django.db.models.fields.CharField', [], {'default': "'\\xe7\\x9b\\xb4\\xe6\\x8a\\xb5\\xe7\\xba\\xa2\\xe5\\x8c\\x85'", 'max_length': '20'}),
            'target_channel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'unavailable_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_reward.wanglibaoactivitygift': {
            'Meta': {'object_name': 'WanglibaoActivityGift'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_activity.Activity']"}),
            'cfg': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_reward.WanglibaoActivityGiftGlobalCfg']"}),
            'chances': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'channels': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'each_day_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gift_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u'\\u7ea2\\u5305'", 'max_length': '128'}),
            'rate': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'redpack': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_redpack.RedPackEvent']"}),
            'send_rate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'wanglibao_reward.wanglibaoactivitygiftglobalcfg': {
            'Meta': {'object_name': 'WanglibaoActivityGiftGlobalCfg'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_activity.Activity']"}),
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'chances': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'terminal_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'when_register': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'wanglibao_reward.wanglibaoactivitygiftorder': {
            'Meta': {'object_name': 'WanglibaoActivityGiftOrder'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'valid_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_reward.wanglibaoactivityreward': {
            'Meta': {'unique_together': "(('user', 'create_at'),)", 'object_name': 'WanglibaoActivityReward'},
            'activity': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'channel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'has_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'join_times': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'left_times': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'p2p_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'qrcode': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'redpack_event': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_redpack.RedPackEvent']", 'null': 'True', 'blank': 'True'}),
            'reward': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['marketing.Reward']", 'null': 'True', 'blank': 'True'}),
            'update_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reward_owner'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True', 'null': 'True'}),
            'when_dist': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_reward.wanglibaousergift': {
            'Meta': {'object_name': 'WanglibaoUserGift'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_activity.Activity']"}),
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'get_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u'\\u7ea2\\u5305'", 'max_length': '128'}),
            'redpack_record_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rules': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['wanglibao_reward.WanglibaoActivityGift']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True'}),
            'valid': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'wanglibao_reward.wanglibaoweixinrelative': {
            'Meta': {'object_name': 'WanglibaoWeixinRelative'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128'}),
            'openid': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'phone_for_fencai': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        }
    }

    complete_apps = ['wanglibao_reward']