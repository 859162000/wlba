# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PhoneValidateCode.vcount'
        db.add_column(u'wanglibao_sms_phonevalidatecode', 'vcount',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PhoneValidateCode.vcount'
        db.delete_column(u'wanglibao_sms_phonevalidatecode', 'vcount')


    models = {
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