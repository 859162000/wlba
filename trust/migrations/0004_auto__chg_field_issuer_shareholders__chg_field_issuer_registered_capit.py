# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Issuer.shareholders'
        db.alter_column(u'trust_issuer', 'shareholders', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.registered_capital'
        db.alter_column(u'trust_issuer', 'registered_capital', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Issuer.geo_region'
        db.alter_column(u'trust_issuer', 'geo_region', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.manager'
        db.alter_column(u'trust_issuer', 'manager', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.founded_at'
        db.alter_column(u'trust_issuer', 'founded_at', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Issuer.note'
        db.alter_column(u'trust_issuer', 'note', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.business_range'
        db.alter_column(u'trust_issuer', 'business_range', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.major_stockholder'
        db.alter_column(u'trust_issuer', 'major_stockholder', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.english_name'
        db.alter_column(u'trust_issuer', 'english_name', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.chairman_of_board'
        db.alter_column(u'trust_issuer', 'chairman_of_board', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.legal_presentative'
        db.alter_column(u'trust_issuer', 'legal_presentative', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Issuer.shareholder_background'
        db.alter_column(u'trust_issuer', 'shareholder_background', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Issuer.shareholders'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.shareholders' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.shareholders'
        db.alter_column(u'trust_issuer', 'shareholders', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.registered_capital'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.registered_capital' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.registered_capital'
        db.alter_column(u'trust_issuer', 'registered_capital', self.gf('django.db.models.fields.IntegerField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.geo_region'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.geo_region' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.geo_region'
        db.alter_column(u'trust_issuer', 'geo_region', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.manager'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.manager' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.manager'
        db.alter_column(u'trust_issuer', 'manager', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.founded_at'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.founded_at' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.founded_at'
        db.alter_column(u'trust_issuer', 'founded_at', self.gf('django.db.models.fields.DateField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.note'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.note' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.note'
        db.alter_column(u'trust_issuer', 'note', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.business_range'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.business_range' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.business_range'
        db.alter_column(u'trust_issuer', 'business_range', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.major_stockholder'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.major_stockholder' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.major_stockholder'
        db.alter_column(u'trust_issuer', 'major_stockholder', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.english_name'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.english_name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.english_name'
        db.alter_column(u'trust_issuer', 'english_name', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.chairman_of_board'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.chairman_of_board' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.chairman_of_board'
        db.alter_column(u'trust_issuer', 'chairman_of_board', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.legal_presentative'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.legal_presentative' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.legal_presentative'
        db.alter_column(u'trust_issuer', 'legal_presentative', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Issuer.shareholder_background'
        raise RuntimeError("Cannot reverse this migration. 'Issuer.shareholder_background' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Issuer.shareholder_background'
        db.alter_column(u'trust_issuer', 'shareholder_background', self.gf('django.db.models.fields.TextField')())

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