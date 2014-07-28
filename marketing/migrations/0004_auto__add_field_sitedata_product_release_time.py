# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SiteData.product_release_time'
        db.add_column(u'marketing_sitedata', 'product_release_time',
                      self.gf('django.db.models.fields.CharField')(default=u'17:30', max_length=128),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SiteData.product_release_time'
        db.delete_column(u'marketing_sitedata', 'product_release_time')


    models = {
        u'marketing.newsandreport': {
            'Meta': {'ordering': "['-score']", 'object_name': 'NewsAndReport'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'marketing.sitedata': {
            'Meta': {'object_name': 'SiteData'},
            'demand_deposit_interest_rate': ('django.db.models.fields.FloatField', [], {'default': '0.35'}),
            'earning_rate': ('django.db.models.fields.CharField', [], {'default': "u'10%-15%'", 'max_length': '16'}),
            'highest_earning_rate': ('django.db.models.fields.FloatField', [], {'default': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invest_threshold': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'one_year_interest_rate': ('django.db.models.fields.FloatField', [], {'default': '3'}),
            'p2p_total_earning': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'p2p_total_trade': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'product_release_time': ('django.db.models.fields.CharField', [], {'default': "u'17:30'", 'max_length': '128'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['marketing']