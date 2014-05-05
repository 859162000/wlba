# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Banner'
        db.create_table(u'wanglibao_banner_banner', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=1024, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('alt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_banner', ['Banner'])


    def backwards(self, orm):
        # Deleting model 'Banner'
        db.delete_table(u'wanglibao_banner_banner')


    models = {
        u'wanglibao_banner.banner': {
            'Meta': {'ordering': "['-priority', '-last_updated']", 'object_name': 'Banner'},
            'alt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['wanglibao_banner']