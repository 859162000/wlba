# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Topic'
        db.create_table(u'wanglibao_help_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'wanglibao_help', ['Topic'])

        # Adding model 'Question'
        db.create_table(u'wanglibao_help_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_help.Topic'], on_delete=models.PROTECT)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('answer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('hotspot', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sortord', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'wanglibao_help', ['Question'])


    def backwards(self, orm):
        # Deleting model 'Topic'
        db.delete_table(u'wanglibao_help_topic')

        # Deleting model 'Question'
        db.delete_table(u'wanglibao_help_question')


    models = {
        u'wanglibao_help.question': {
            'Meta': {'object_name': 'Question'},
            'answer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hotspot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sortord': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_help.Topic']", 'on_delete': 'models.PROTECT'})
        },
        u'wanglibao_help.topic': {
            'Meta': {'object_name': 'Topic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['wanglibao_help']