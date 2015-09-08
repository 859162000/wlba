# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AntiDelayCallback'
        db.create_table(u'wanglibao_anti_antidelaycallback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.IntegerField')()),
            ('createtime', self.gf('django.db.models.fields.IntegerField')()),
            ('updatetime', self.gf('django.db.models.fields.IntegerField')()),
            ('channel', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('device', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'wanglibao_anti', ['AntiDelayCallback'])


    def backwards(self, orm):
        # Deleting model 'AntiDelayCallback'
        db.delete_table(u'wanglibao_anti_antidelaycallback')


    models = {
        u'wanglibao_anti.antidelaycallback': {
            'Meta': {'object_name': 'AntiDelayCallback'},
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'createtime': ('django.db.models.fields.IntegerField', [], {}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'uid': ('django.db.models.fields.IntegerField', [], {}),
            'updatetime': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['wanglibao_anti']