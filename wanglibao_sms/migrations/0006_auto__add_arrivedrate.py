# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ArrivedRate'
        db.create_table(u'wanglibao_sms_arrivedrate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('achieved', self.gf('django.db.models.fields.IntegerField')()),
            ('total_amount', self.gf('django.db.models.fields.IntegerField')()),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('start', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('end', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_sms', ['ArrivedRate'])


    def backwards(self, orm):
        # Deleting model 'ArrivedRate'
        db.delete_table(u'wanglibao_sms_arrivedrate')


    models = {
        u'wanglibao_sms.arrivedrate': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'ArrivedRate'},
            'achieved': ('django.db.models.fields.IntegerField', [], {}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'start': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'total_amount': ('django.db.models.fields.IntegerField', [], {})
        },
        u'wanglibao_sms.phonevalidatecode': {
            'Meta': {'ordering': "['-last_send_time']", 'object_name': 'PhoneValidateCode'},
            'code_send_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_send_time': ('django.db.models.fields.DateTimeField', [], {}),
            'phone': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'validate_code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'validate_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vcount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_sms.ratethrottle': {
            'Meta': {'object_name': 'RateThrottle'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '24', 'db_index': 'True'}),
            'last_send_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'max_count': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'send_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'wanglibao_sms.shortmessage': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'ShortMessage'},
            'channel': ('django.db.models.fields.CharField', [], {'default': "u'\\u6162\\u9053'", 'max_length': '10'}),
            'contents': ('django.db.models.fields.TextField', [], {}),
            'context': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phones': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u53d1\\u9001\\u4e2d'", 'max_length': '8'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'\\u7cfb\\u7edf'", 'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_sms']