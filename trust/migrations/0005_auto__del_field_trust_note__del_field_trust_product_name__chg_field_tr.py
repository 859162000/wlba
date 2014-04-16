# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Trust.note'
        db.delete_column(u'trust_trust', 'note')

        # Deleting field 'Trust.product_name'
        db.delete_column(u'trust_trust', 'product_name')


        # Changing field 'Trust.period'
        db.alter_column(u'trust_trust', 'period', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Trust.earning_description'
        db.alter_column(u'trust_trust', 'earning_description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trust.available_region'
        db.alter_column(u'trust_trust', 'available_region', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trust.issue_date'
        db.alter_column(u'trust_trust', 'issue_date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Trust.scale'
        db.alter_column(u'trust_trust', 'scale', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Trust.brief'
        db.alter_column(u'trust_trust', 'brief', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trust.usage'
        db.alter_column(u'trust_trust', 'usage', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Trust.type'
        db.alter_column(u'trust_trust', 'type', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trust.related_info'
        db.alter_column(u'trust_trust', 'related_info', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trust.risk_management'
        db.alter_column(u'trust_trust', 'risk_management', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trust.investment_threshold'
        db.alter_column(u'trust_trust', 'investment_threshold', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Trust.usage_description'
        db.alter_column(u'trust_trust', 'usage_description', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Trust.note'
        raise RuntimeError("Cannot reverse this migration. 'Trust.note' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Trust.note'
        db.add_column(u'trust_trust', 'note',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Trust.product_name'
        raise RuntimeError("Cannot reverse this migration. 'Trust.product_name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Trust.product_name'
        db.add_column(u'trust_trust', 'product_name',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Trust.period'
        raise RuntimeError("Cannot reverse this migration. 'Trust.period' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.period'
        db.alter_column(u'trust_trust', 'period', self.gf('django.db.models.fields.FloatField')())

        # User chose to not deal with backwards NULL issues for 'Trust.earning_description'
        raise RuntimeError("Cannot reverse this migration. 'Trust.earning_description' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.earning_description'
        db.alter_column(u'trust_trust', 'earning_description', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Trust.available_region'
        raise RuntimeError("Cannot reverse this migration. 'Trust.available_region' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.available_region'
        db.alter_column(u'trust_trust', 'available_region', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Trust.issue_date'
        raise RuntimeError("Cannot reverse this migration. 'Trust.issue_date' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.issue_date'
        db.alter_column(u'trust_trust', 'issue_date', self.gf('django.db.models.fields.DateField')())

        # User chose to not deal with backwards NULL issues for 'Trust.scale'
        raise RuntimeError("Cannot reverse this migration. 'Trust.scale' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.scale'
        db.alter_column(u'trust_trust', 'scale', self.gf('django.db.models.fields.IntegerField')())

        # User chose to not deal with backwards NULL issues for 'Trust.brief'
        raise RuntimeError("Cannot reverse this migration. 'Trust.brief' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.brief'
        db.alter_column(u'trust_trust', 'brief', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Trust.usage'
        raise RuntimeError("Cannot reverse this migration. 'Trust.usage' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.usage'
        db.alter_column(u'trust_trust', 'usage', self.gf('django.db.models.fields.CharField')(max_length=100))

        # User chose to not deal with backwards NULL issues for 'Trust.type'
        raise RuntimeError("Cannot reverse this migration. 'Trust.type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.type'
        db.alter_column(u'trust_trust', 'type', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Trust.related_info'
        raise RuntimeError("Cannot reverse this migration. 'Trust.related_info' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.related_info'
        db.alter_column(u'trust_trust', 'related_info', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Trust.risk_management'
        raise RuntimeError("Cannot reverse this migration. 'Trust.risk_management' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.risk_management'
        db.alter_column(u'trust_trust', 'risk_management', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Trust.investment_threshold'
        raise RuntimeError("Cannot reverse this migration. 'Trust.investment_threshold' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.investment_threshold'
        db.alter_column(u'trust_trust', 'investment_threshold', self.gf('django.db.models.fields.FloatField')())

        # User chose to not deal with backwards NULL issues for 'Trust.usage_description'
        raise RuntimeError("Cannot reverse this migration. 'Trust.usage_description' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Trust.usage_description'
        db.alter_column(u'trust_trust', 'usage_description', self.gf('django.db.models.fields.TextField')())

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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'type': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'usage_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['trust']