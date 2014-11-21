# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Announcement.createtime'
        db.add_column(u'wanglibao_announcement_announcement', 'createtime',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 10, 27, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Announcement.createtime'
        db.delete_column(u'wanglibao_announcement_announcement', 'createtime')


    models = {
        u'wanglibao_announcement.announcement': {
            'Meta': {'ordering': "['-priority', '-updatetime']", 'object_name': 'Announcement'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'createtime': ('django.db.models.fields.DateTimeField', [], {}),
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