# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Trust.bought_people_count'
        db.add_column(u'trust_trust', 'bought_people_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Trust.bought_count'
        db.add_column(u'trust_trust', 'bought_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Trust.bought_amount'
        db.add_column(u'trust_trust', 'bought_amount',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Trust.bought_people_count'
        db.delete_column(u'trust_trust', 'bought_people_count')

        # Deleting field 'Trust.bought_count'
        db.delete_column(u'trust_trust', 'bought_count')

        # Deleting field 'Trust.bought_amount'
        db.delete_column(u'trust_trust', 'bought_amount')


    models = {
        u'trust.issuer': {
            'Meta': {'object_name': 'Issuer'},
            'appear_on_market': ('django.db.models.fields.BooleanField', [], {}),
            'business_range': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'chairman_of_board': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'english_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'founded_at': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'geo_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legal_presentative': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'major_stockholder': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'registered_capital': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shareholder_background': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'shareholders': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.TextField', [], {})
        },
        u'trust.trust': {
            'Meta': {'object_name': 'Trust'},
            'available_region': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'bought_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'bought_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bought_people_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'consignee': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'earning_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {}),
            'financing_party': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'financing_party_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'guarantee': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_method': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'issue_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trust.Issuer']"}),
            'mortgage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'mortgage_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'payment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'period': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'product_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'related_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'risk_management': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scale': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'source_of_repayment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5728\\u552e'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'usage_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['trust']