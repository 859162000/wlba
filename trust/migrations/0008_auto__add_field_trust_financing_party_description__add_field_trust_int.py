# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Trust.financing_party_description'
        db.add_column(u'trust_trust', 'financing_party_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Trust.interest_method'
        db.add_column(u'trust_trust', 'interest_method',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=25, blank=True),
                      keep_default=False)


        # Changing field 'Trust.financing_party'
        db.alter_column(u'trust_trust', 'financing_party', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):
        # Deleting field 'Trust.financing_party_description'
        db.delete_column(u'trust_trust', 'financing_party_description')

        # Deleting field 'Trust.interest_method'
        db.delete_column(u'trust_trust', 'interest_method')


        # Changing field 'Trust.financing_party'
        db.alter_column(u'trust_trust', 'financing_party', self.gf('django.db.models.fields.TextField')())

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