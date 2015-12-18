# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PhoneValidateCode.last_validate_time'
        db.add_column(u'wanglibao_sms_phonevalidatecode', 'last_validate_time',
                      self.gf('django.db.models.fields.DateTimeField')(default='2015-12-01T00:00:00+08:00', db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PhoneValidateCode.last_validate_time'
        db.delete_column(u'wanglibao_sms_phonevalidatecode', 'last_validate_time')


    models = {
        u'wanglibao_sms.arrivedrate': {
            'Meta': {'ordering': "['-created_at']", 'unique_together': "(('channel', 'start'),)", 'object_name': 'ArrivedRate'},
            'achieved': ('django.db.models.fields.IntegerField', [], {}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'start': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'total_amount': ('django.db.models.fields.IntegerField', [], {})
        },
        u'wanglibao_sms.messagetemplate': {
            'Meta': {'ordering': "['id']", 'object_name': 'MessageTemplate'},
            'args_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'args_tips': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_for': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        u'wanglibao_sms.phonevalidatecode': {
            'Meta': {'ordering': "['-last_send_time']", 'object_name': 'PhoneValidateCode'},
            'code_send_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': "'2015-12-01T00:00:00+08:00'", 'db_index': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_send_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'last_validate_time': ('django.db.models.fields.DateTimeField', [], {'default': "'2015-12-01T00:00:00+08:00'", 'db_index': 'True'}),
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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phones': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u53d1\\u9001\\u4e2d'", 'max_length': '8'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'\\u7cfb\\u7edf'", 'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_sms']