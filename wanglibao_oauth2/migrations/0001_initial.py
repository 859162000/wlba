# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Client'
        db.create_table(u'wanglibao_oauth2_client', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client_id', self.gf('django.db.models.fields.CharField')(default='4d5b7f13e1cbb1d94052', unique=True, max_length=255, db_index=True)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(default='c6bd4dff3669c62b7bebbcb82c02f62052636bfe', max_length=255)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marketing.Channels'], null=True, blank=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_oauth2', ['Client'])

        # Adding model 'AccessToken'
        db.create_table(u'wanglibao_oauth2_accesstoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('token', self.gf('django.db.models.fields.CharField')(default='e1e60b8e95c1ad4affe6071d21b9a6c60844a1e9', max_length=255, db_index=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_oauth2.Client'])),
            ('expires', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'wanglibao_oauth2', ['AccessToken'])

        # Adding model 'RefreshToken'
        db.create_table(u'wanglibao_oauth2_refreshtoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('token', self.gf('django.db.models.fields.CharField')(default='5d51f26ef790a8f59fac7a5f6b93cb82c08b59fb', max_length=255)),
            ('access_token', self.gf('django.db.models.fields.related.OneToOneField')(related_name='refresh_token', unique=True, to=orm['wanglibao_oauth2.AccessToken'])),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_oauth2.Client'])),
            ('expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wanglibao_oauth2', ['RefreshToken'])


    def backwards(self, orm):
        # Deleting model 'Client'
        db.delete_table(u'wanglibao_oauth2_client')

        # Deleting model 'AccessToken'
        db.delete_table(u'wanglibao_oauth2_accesstoken')

        # Deleting model 'RefreshToken'
        db.delete_table(u'wanglibao_oauth2_refreshtoken')


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
        u'marketing.channels': {
            'Meta': {'object_name': 'Channels'},
            'classification': ('django.db.models.fields.CharField', [], {'default': "'----'", 'max_length': '20'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'coop_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'is_abandoned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'merge_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': "'full'", 'max_length': '20'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'wanglibao_oauth2.accesstoken': {
            'Meta': {'object_name': 'AccessToken'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_oauth2.Client']"}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'7671b8c7c2be4744270fe7779afb8d9facddabc2'", 'max_length': '255', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_oauth2.client': {
            'Meta': {'object_name': 'Client'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.Channels']", 'null': 'True', 'blank': 'True'}),
            'client_id': ('django.db.models.fields.CharField', [], {'default': "'eb725bdd5c0a2fa52a17'", 'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'default': "'808cd0f0470e39b51503dfe0f3ad7822949c0683'", 'max_length': '255'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_oauth2.refreshtoken': {
            'Meta': {'object_name': 'RefreshToken'},
            'access_token': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'refresh_token'", 'unique': 'True', 'to': u"orm['wanglibao_oauth2.AccessToken']"}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_oauth2.Client']"}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'7f2c43c4406b61e89427006d920448dcda49318d'", 'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['wanglibao_oauth2']