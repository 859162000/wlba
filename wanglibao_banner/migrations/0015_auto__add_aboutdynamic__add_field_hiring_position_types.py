# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AboutDynamic'
        db.create_table(u'wanglibao_banner_aboutdynamic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('content', self.gf('ckeditor.fields.RichTextField')()),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('hide_in_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'wanglibao_banner', ['AboutDynamic'])

        # Adding field 'Hiring.position_types'
        db.add_column(u'wanglibao_banner_hiring', 'position_types',
                      self.gf('django.db.models.fields.CharField')(default=u'\u5168\u90e8', max_length=20),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'AboutDynamic'
        db.delete_table(u'wanglibao_banner_aboutdynamic')

        # Deleting field 'Hiring.position_types'
        db.delete_column(u'wanglibao_banner_hiring', 'position_types')


    models = {
        u'wanglibao_banner.aboutdynamic': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'AboutDynamic'},
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hide_in_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'wanglibao_banner.aboutus': {
            'Meta': {'object_name': 'Aboutus'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'content': ('ckeditor.fields.RichTextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'wanglibao_banner.appactivate': {
            'Meta': {'object_name': 'AppActivate'},
            'device': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_four': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'img_one': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'img_three': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'img_two': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_long_used': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jump_state': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link_dest': ('django.db.models.fields.CharField', [], {'default': "u'3'", 'max_length': '32'}),
            'link_dest_h5_url': ('django.db.models.fields.CharField', [], {'default': "u'https://'", 'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'pc_redirect_url': ('django.db.models.fields.CharField', [], {'default': "u'http://'", 'max_length': '300'}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user_invest_limit': ('django.db.models.fields.CharField', [], {'default': "u'-1'", 'max_length': '8'})
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
            'position_types': ('django.db.models.fields.CharField', [], {'default': "u'\\u5168\\u90e8'", 'max_length': '20'}),
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