# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Issuer'
        db.create_table(u'trust_issuer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('short_name', self.gf('django.db.models.fields.TextField')()),
            ('english_name', self.gf('django.db.models.fields.TextField')()),
            ('registered_capital', self.gf('django.db.models.fields.IntegerField')()),
            ('legal_presentative', self.gf('django.db.models.fields.TextField')()),
            ('chairman_of_board', self.gf('django.db.models.fields.TextField')()),
            ('manager', self.gf('django.db.models.fields.TextField')()),
            ('founded_at', self.gf('django.db.models.fields.DateField')()),
            ('appear_on_market', self.gf('django.db.models.fields.BooleanField')()),
            ('geo_region', self.gf('django.db.models.fields.TextField')()),
            ('shareholder_background', self.gf('django.db.models.fields.TextField')()),
            ('major_stockholder', self.gf('django.db.models.fields.TextField')()),
            ('shareholders', self.gf('django.db.models.fields.TextField')()),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('business_range', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'trust', ['Issuer'])

        # Adding model 'Trust'
        db.create_table(u'trust_trust', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('expected_earning_rate', self.gf('django.db.models.fields.FloatField')()),
            ('brief', self.gf('django.db.models.fields.TextField')()),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trust.Issuer'])),
            ('available_region', self.gf('django.db.models.fields.TextField')()),
            ('scale', self.gf('django.db.models.fields.IntegerField')()),
            ('investment_threshold', self.gf('django.db.models.fields.FloatField')()),
            ('period', self.gf('django.db.models.fields.FloatField')()),
            ('issue_date', self.gf('django.db.models.fields.DateField')()),
            ('type', self.gf('django.db.models.fields.TextField')()),
            ('earning_description', self.gf('django.db.models.fields.TextField')()),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('usage_description', self.gf('django.db.models.fields.TextField')()),
            ('risk_management', self.gf('django.db.models.fields.TextField')()),
            ('payment', self.gf('django.db.models.fields.TextField')()),
            ('product_name', self.gf('django.db.models.fields.TextField')()),
            ('related_info', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'trust', ['Trust'])


    def backwards(self, orm):
        # Deleting model 'Issuer'
        db.delete_table(u'trust_issuer')

        # Deleting model 'Trust'
        db.delete_table(u'trust_trust')


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
            'earning_description': ('django.db.models.fields.TextField', [], {}),
            'expected_earning_rate': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {}),
            'issue_date': ('django.db.models.fields.DateField', [], {}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trust.Issuer']"}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'payment': ('django.db.models.fields.TextField', [], {}),
            'period': ('django.db.models.fields.FloatField', [], {}),
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