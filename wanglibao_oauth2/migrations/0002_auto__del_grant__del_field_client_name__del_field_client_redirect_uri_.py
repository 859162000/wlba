# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Grant'
        db.delete_table(u'wanglibao_oauth2_grant')

        # Deleting field 'Client.name'
        db.delete_column(u'wanglibao_oauth2_client', 'name')

        # Deleting field 'Client.redirect_uri'
        db.delete_column(u'wanglibao_oauth2_client', 'redirect_uri')

        # Deleting field 'Client.url'
        db.delete_column(u'wanglibao_oauth2_client', 'url')

        # Deleting field 'Client.user'
        db.delete_column(u'wanglibao_oauth2_client', 'user_id')

        # Deleting field 'Client.client_type'
        db.delete_column(u'wanglibao_oauth2_client', 'client_type')

        # Adding field 'Client.channel_code'
        db.add_column(u'wanglibao_oauth2_client', 'channel_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=12),
                      keep_default=False)

        # Adding field 'Client.channel'
        db.add_column(u'wanglibao_oauth2_client', 'channel',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marketing.Channels'], null=True, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'Client', fields ['client_id']
        db.create_unique(u'wanglibao_oauth2_client', ['client_id'])

        # Deleting field 'AccessToken.scope'
        db.delete_column(u'wanglibao_oauth2_accesstoken', 'scope')


    def backwards(self, orm):
        # Removing unique constraint on 'Client', fields ['client_id']
        db.delete_unique(u'wanglibao_oauth2_client', ['client_id'])

        # Adding model 'Grant'
        db.create_table(u'wanglibao_oauth2_grant', (
            ('code', self.gf('django.db.models.fields.CharField')(default='806afe87274f6f36b09393d290540f1d7240da02', max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('redirect_uri', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('scope', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 10, 20, 0, 0))),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_oauth2.Client'])),
        ))
        db.send_create_signal(u'wanglibao_oauth2', ['Grant'])

        # Adding field 'Client.name'
        db.add_column(u'wanglibao_oauth2_client', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Client.redirect_uri'
        db.add_column(u'wanglibao_oauth2_client', 'redirect_uri',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Client.url'
        db.add_column(u'wanglibao_oauth2_client', 'url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Client.user'
        db.add_column(u'wanglibao_oauth2_client', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='oauth2_client', null=True, to=orm['auth.User'], blank=True),
                      keep_default=False)

        # Adding field 'Client.client_type'
        db.add_column(u'wanglibao_oauth2_client', 'client_type',
                      self.gf('django.db.models.fields.IntegerField')(default=''),
                      keep_default=False)

        # Deleting field 'Client.channel_code'
        db.delete_column(u'wanglibao_oauth2_client', 'channel_code')

        # Deleting field 'Client.channel'
        db.delete_column(u'wanglibao_oauth2_client', 'channel_id')

        # Adding field 'AccessToken.scope'
        db.add_column(u'wanglibao_oauth2_accesstoken', 'scope',
                      self.gf('django.db.models.fields.IntegerField')(default=2),
                      keep_default=False)


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
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'})
        },
        u'wanglibao_oauth2.accesstoken': {
            'Meta': {'object_name': 'AccessToken'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_oauth2.Client']"}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'796d74f537d5c3224c0c216d1479fe16d82c9e2e'", 'max_length': '255', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wanglibao_oauth2.client': {
            'Meta': {'object_name': 'Client'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marketing.Channels']", 'null': 'True', 'blank': 'True'}),
            'channel_code': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'client_id': ('django.db.models.fields.CharField', [], {'default': "'1c62110d7b9b15cf71dd'", 'unique': 'True', 'max_length': '255'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'default': "'6256c4bc030cb53ee942042e54ac58a6a4ebbc03'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wanglibao_oauth2.refreshtoken': {
            'Meta': {'object_name': 'RefreshToken'},
            'access_token': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'refresh_token'", 'unique': 'True', 'to': u"orm['wanglibao_oauth2.AccessToken']"}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_oauth2.Client']"}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'d3b96798a088df9ea215b23fb4fc332feafcdd30'", 'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['wanglibao_oauth2']