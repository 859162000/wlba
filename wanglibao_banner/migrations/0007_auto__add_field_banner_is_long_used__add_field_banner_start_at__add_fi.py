# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Banner.is_long_used'
        db.add_column(u'wanglibao_banner_banner', 'is_long_used',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Banner.start_at'
        db.add_column(u'wanglibao_banner_banner', 'start_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Banner.end_at'
        db.add_column(u'wanglibao_banner_banner', 'end_at',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Banner.is_used'
        db.add_column(u'wanglibao_banner_banner', 'is_used',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Banner.is_long_used'
        db.delete_column(u'wanglibao_banner_banner', 'is_long_used')

        # Deleting field 'Banner.start_at'
        db.delete_column(u'wanglibao_banner_banner', 'start_at')

        # Deleting field 'Banner.end_at'
        db.delete_column(u'wanglibao_banner_banner', 'end_at')

        # Deleting field 'Banner.is_used'
        db.delete_column(u'wanglibao_banner_banner', 'is_used')


    models = {
        u'wanglibao_banner.aboutus': {
            'Meta': {'object_name': 'Aboutus'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'content': ('ckeditor.fields.RichTextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'wanglibao_banner.banner': {
            'Meta': {'ordering': "['-priority', '-last_updated']", 'object_name': 'Banner'},
            'alt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_long_used': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        u'wanglibao_banner.hiring': {
            'Meta': {'ordering': "['-priority', '-last_updated']", 'object_name': 'Hiring'},
            'duties': ('ckeditor.fields.RichTextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_urgent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'requirements': ('ckeditor.fields.RichTextField', [], {})
        },
        u'wanglibao_banner.partner': {
            'Meta': {'ordering': "['-priority', '-last_updated']", 'object_name': 'Partner'},
            'alt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "u'http://'", 'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['wanglibao_banner']