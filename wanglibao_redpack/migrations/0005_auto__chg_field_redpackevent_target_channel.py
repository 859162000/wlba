# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'RedPackEvent.target_channel'
        db.alter_column(u'wanglibao_redpack_redpackevent', 'target_channel', self.gf('django.db.models.fields.CharField')(max_length=1000))

    def backwards(self, orm):

        # Changing field 'RedPackEvent.target_channel'
        db.alter_column(u'wanglibao_redpack_redpackevent', 'target_channel', self.gf('django.db.models.fields.CharField')(max_length=20))

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
        u'wanglibao_redpack.redpack': {
            'Meta': {'object_name': 'RedPack'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.RedPackEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unused'", 'max_length': '20'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'db_index': 'True'})
        },
        u'wanglibao_redpack.redpackevent': {
            'Meta': {'object_name': 'RedPackEvent'},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x85\\xa8\\xe5\\xb9\\xb3\\xe5\\x8f\\xb0'", 'max_length': '10'}),
            'available_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'describe': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'give_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'give_mode': ('django.db.models.fields.CharField', [], {'default': "'\\xe6\\xb3\\xa8\\xe5\\x86\\x8c'", 'max_length': '20', 'db_index': 'True'}),
            'give_platform': ('django.db.models.fields.CharField', [], {'default': "'\\xe5\\x85\\xa8\\xe5\\xb9\\xb3\\xe5\\x8f\\xb0'", 'max_length': '10'}),
            'give_start_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'highest_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invest_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'rtype': ('django.db.models.fields.CharField', [], {'default': "'\\xe7\\x9b\\xb4\\xe6\\x8a\\xb5\\xe7\\xba\\xa2\\xe5\\x8c\\x85'", 'max_length': '20'}),
            'target_channel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'unavailable_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_redpack.redpackrecord': {
            'Meta': {'object_name': 'RedPackRecord'},
            'apply_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'apply_platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'change_platform': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'redpack': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_redpack.RedPack']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['wanglibao_redpack']