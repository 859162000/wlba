# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {
        u'wanglibao_anti.antidelaycallback': {
            'Meta': {'object_name': 'AntiDelayCallback', 'db_table': "'anti_delay_callback'", 'managed': 'False'},
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'createtime': ('django.db.models.fields.IntegerField', [], {}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'updatetime': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['wanglibao_anti']