# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Announcement'
        db.create_table(u'wanglibao_announcement_announcement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.CharField')(default='pc', max_length=15)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('content', self.gf('ckeditor.fields.RichTextField')()),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('hideinlist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('endtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, max_length=2)),
            ('updatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_announcement', ['Announcement'])


    def backwards(self, orm):
        # Deleting model 'Announcement'
        db.delete_table(u'wanglibao_announcement_announcement')


    models = {
        u'wanglibao_announcement.announcement': {
            'Meta': {'ordering': "['-priority', '-updatetime']", 'object_name': 'Announcement'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
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
        }
    }

    complete_apps = ['wanglibao_announcement']