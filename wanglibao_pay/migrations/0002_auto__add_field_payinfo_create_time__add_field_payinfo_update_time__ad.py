# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PayInfo.create_time'
        db.add_column(u'wanglibao_pay_payinfo', 'create_time',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 6, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.update_time'
        db.add_column(u'wanglibao_pay_payinfo', 'update_time',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2014, 6, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.request'
        db.add_column(u'wanglibao_pay_payinfo', 'request',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.response'
        db.add_column(u'wanglibao_pay_payinfo', 'response',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.status'
        db.add_column(u'wanglibao_pay_payinfo', 'status',
                      self.gf('django.db.models.fields.CharField')(default=u'\xe6\x88\x90\xe5\x8a\x9f', max_length=15),
                      keep_default=False)

        # Adding field 'PayInfo.error_code'
        db.add_column(u'wanglibao_pay_payinfo', 'error_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'PayInfo.error_message'
        db.add_column(u'wanglibao_pay_payinfo', 'error_message',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)


        # Changing field 'PayInfo.amount'
        db.alter_column(u'wanglibao_pay_payinfo', 'amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2))

    def backwards(self, orm):
        # Deleting field 'PayInfo.create_time'
        db.delete_column(u'wanglibao_pay_payinfo', 'create_time')

        # Deleting field 'PayInfo.update_time'
        db.delete_column(u'wanglibao_pay_payinfo', 'update_time')

        # Deleting field 'PayInfo.request'
        db.delete_column(u'wanglibao_pay_payinfo', 'request')

        # Deleting field 'PayInfo.response'
        db.delete_column(u'wanglibao_pay_payinfo', 'response')

        # Deleting field 'PayInfo.status'
        db.delete_column(u'wanglibao_pay_payinfo', 'status')

        # Deleting field 'PayInfo.error_code'
        db.delete_column(u'wanglibao_pay_payinfo', 'error_code')

        # Deleting field 'PayInfo.error_message'
        db.delete_column(u'wanglibao_pay_payinfo', 'error_message')


        # Changing field 'PayInfo.amount'
        db.alter_column(u'wanglibao_pay_payinfo', 'amount', self.gf('django.db.models.fields.FloatField')())

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
        u'wanglibao_pay.payinfo': {
            'Meta': {'object_name': 'PayInfo'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['wanglibao_pay']