# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Banner.link'
        db.alter_column(u'wanglibao_banner_banner', 'link', self.gf('django.db.models.fields.CharField')(max_length=1024))

    def backwards(self, orm):

        # Changing field 'Banner.link'
        db.alter_column(u'wanglibao_banner_banner', 'link', self.gf('django.db.models.fields.URLField')(max_length=1024))

    models = {
        u'wanglibao_banner.banner': {
            'Meta': {'ordering': "['-priority', '-last_updated']", 'object_name': 'Banner'},
            'alt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['wanglibao_banner']