# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'WanglibaoUserProfile.identity_type'
        db.delete_column(u'wanglibao_profile_wanglibaouserprofile', 'identity_type')

        # Deleting field 'WanglibaoUserProfile.identity'
        db.delete_column(u'wanglibao_profile_wanglibaouserprofile', 'identity')

        # Adding field 'WanglibaoUserProfile.nick_name'
        db.add_column(u'wanglibao_profile_wanglibaouserprofile', 'nick_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'WanglibaoUserProfile.identity_type'
        db.add_column(u'wanglibao_profile_wanglibaouserprofile', 'identity_type',
                      self.gf('django.db.models.fields.CharField')(default='id', max_length=10),
                      keep_default=False)

        # Adding field 'WanglibaoUserProfile.identity'
        db.add_column(u'wanglibao_profile_wanglibaouserprofile', 'identity',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)

        # Deleting field 'WanglibaoUserProfile.nick_name'
        db.delete_column(u'wanglibao_profile_wanglibaouserprofile', 'nick_name')


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
        u'wanglibao_profile.wanglibaouserprofile': {
            'Meta': {'object_name': 'WanglibaoUserProfile'},
            'investment_asset': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'phone_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'risk_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'total_asset': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['wanglibao_profile']