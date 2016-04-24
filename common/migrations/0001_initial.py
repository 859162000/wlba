# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CallbackRecord'
        db.create_table(u'common_callbackrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('callback_to', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('order_id', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('third_order_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, null=True, blank=True)),
            ('result_code', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('result_msg', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('result_errors', self.gf('django.db.models.fields.TextField')(max_length=500, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=255, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('answer_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('request_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('request_data', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('request_headers', self.gf('django.db.models.fields.TextField')(max_length=255, null=True, blank=True)),
            ('request_action', self.gf('django.db.models.fields.CharField')(default=1, max_length=2)),
            ('ret_parser', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('extra', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('re_callback', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'common', ['CallbackRecord'])

        # Adding unique constraint on 'CallbackRecord', fields ['callback_to', 'order_id']
        db.create_unique(u'common_callbackrecord', ['callback_to', 'order_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CallbackRecord', fields ['callback_to', 'order_id']
        db.delete_unique(u'common_callbackrecord', ['callback_to', 'order_id'])

        # Deleting model 'CallbackRecord'
        db.delete_table(u'common_callbackrecord')


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
        u'common.callbackrecord': {
            'Meta': {'unique_together': "(('callback_to', 'order_id'),)", 'object_name': 'CallbackRecord'},
            'answer_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'callback_to': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'extra': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            're_callback': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'request_action': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '2'}),
            'request_data': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'request_headers': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'request_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'result_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'result_errors': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'result_msg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ret_parser': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'third_order_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['common']