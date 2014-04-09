# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Issuer.logo'
        db.add_column(u'trust_issuer', 'logo',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Issuer.logo'
        db.delete_column(u'trust_issuer', 'logo')


    models = {
        u'trust.issuer': {
            'Meta': {'object_name': 'Issuer'},
            'appear_on_market': ('django.db.models.fields.BooleanField', [], {}),
            'business_range': ('django.db.models.fields.TextField', [], {}),
            'chairman_of_board': ('django.db.models.fields.TextField', [], {}),
            'english_name': ('django.db.models.fields.TextField', [], {}),
            'founded_at': ('django.db.models.fields.DateField', [], {}),
            'geo_region': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legal_presentative': ('django.db.models.fields.TextField', [], {}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'major_stockholder': ('django.db.models.fields.TextField', [], {}),
            'manager': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'registered_capital': ('django.db.models.fields.IntegerField', [], {}),
            'shareholder_background': ('django.db.models.fields.TextField', [], {}),
            'shareholders': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.TextField', [], {})
        },
        u'trust.trust': {
            'Meta': {'object_name': 'Trust'},
            'available_region': ('django.db.models.fields.TextField', [], {}),
            'brief': ('django.db.models.fields.TextField', [], {}),
            'consignee': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'earning_description': ('django.db.models.fields.TextField', [], {}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trust.Issuer']"}),
            'mortgage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mortgage_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'payment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'period': ('django.db.models.fields.FloatField', [], {}),
            'product_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'product_name': ('django.db.models.fields.TextField', [], {}),
            'related_info': ('django.db.models.fields.TextField', [], {}),
            'risk_management': ('django.db.models.fields.TextField', [], {}),
            'scale': ('django.db.models.fields.IntegerField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'type': ('django.db.models.fields.TextField', [], {}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'usage_description': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['trust']