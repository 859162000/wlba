# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AppMemorabilia'
        db.create_table(u'wanglibao_announcement_appmemorabilia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('banner', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('detail_link', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('done_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, max_length=2)),
        ))
        db.send_create_signal(u'wanglibao_announcement', ['AppMemorabilia'])


    def backwards(self, orm):
        # Deleting model 'AppMemorabilia'
        db.delete_table(u'wanglibao_announcement_appmemorabilia')


    models = {
        u'wanglibao_announcement.announcement': {
            'Meta': {'ordering': "['-createtime']", 'object_name': 'Announcement'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'device': ('django.db.models.fields.CharField', [], {'default': "'pc'", 'max_length': '15'}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hideinlist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'max_length': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'updatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'wanglibao_announcement.appmemorabilia': {
            'Meta': {'object_name': 'AppMemorabilia'},
            'banner': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'detail_link': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'done_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'max_length': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['wanglibao_announcement']