# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'AntiDelayCallback', fields ['status']
        db.create_index(u'wanglibao_anti_antidelaycallback', ['status'])

        # Adding index on 'AntiDelayCallback', fields ['ip']
        db.create_index(u'wanglibao_anti_antidelaycallback', ['ip'])

        # Adding index on 'AntiDelayCallback', fields ['channel']
        db.create_index(u'wanglibao_anti_antidelaycallback', ['channel'])


    def backwards(self, orm):
        # Removing index on 'AntiDelayCallback', fields ['channel']
        db.delete_index(u'wanglibao_anti_antidelaycallback', ['channel'])

        # Removing index on 'AntiDelayCallback', fields ['ip']
        db.delete_index(u'wanglibao_anti_antidelaycallback', ['ip'])

        # Removing index on 'AntiDelayCallback', fields ['status']
        db.delete_index(u'wanglibao_anti_antidelaycallback', ['status'])


    models = {
        u'wanglibao_anti.antidelaycallback': {
            'Meta': {'object_name': 'AntiDelayCallback'},
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'createtime': ('django.db.models.fields.IntegerField', [], {}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'\\xe6\\xad\\xa3\\xe5\\xb8\\xb8\\xe7\\x94\\xa8\\xe6\\x88\\xb7'", 'db_index': 'True'}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'updatetime': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['wanglibao_anti']