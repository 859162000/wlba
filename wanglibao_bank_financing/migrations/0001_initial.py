# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bank'
        db.create_table(u'wanglibao_bank_financing_bank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('home_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'wanglibao_bank_financing', ['Bank'])

        # Adding model 'BankFinancing'
        db.create_table(u'wanglibao_bank_financing_bankfinancing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('product_code', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('bank', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wanglibao_bank_financing.Bank'])),
            ('period', self.gf('django.db.models.fields.FloatField')()),
            ('max_expected_profit_rate', self.gf('django.db.models.fields.FloatField')()),
            ('risk_level', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('sale_start_date', self.gf('django.db.models.fields.DateField')()),
            ('sale_end_date', self.gf('django.db.models.fields.DateField')()),
            ('profit_start_date', self.gf('django.db.models.fields.DateField')()),
            ('profit_end_date', self.gf('django.db.models.fields.DateField')()),
            ('profit_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('product_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('principle_guaranteed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invest_threshold', self.gf('django.db.models.fields.FloatField')()),
            ('invest_step', self.gf('django.db.models.fields.FloatField')()),
            ('invest_method', self.gf('django.db.models.fields.TextField')()),
            ('face_value', self.gf('django.db.models.fields.FloatField')()),
            ('region', self.gf('django.db.models.fields.TextField')()),
            ('profit_target', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('profit_rate', self.gf('django.db.models.fields.FloatField')()),
            ('profit_calculation', self.gf('django.db.models.fields.TextField')()),
            ('invest_target', self.gf('django.db.models.fields.TextField')()),
            ('related_target', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'wanglibao_bank_financing', ['BankFinancing'])


    def backwards(self, orm):
        # Deleting model 'Bank'
        db.delete_table(u'wanglibao_bank_financing_bank')

        # Deleting model 'BankFinancing'
        db.delete_table(u'wanglibao_bank_financing_bankfinancing')


    models = {
        u'wanglibao_bank_financing.bank': {
            'Meta': {'object_name': 'Bank'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_bank_financing.bankfinancing': {
            'Meta': {'object_name': 'BankFinancing'},
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_bank_financing.Bank']"}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'face_value': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invest_method': ('django.db.models.fields.TextField', [], {}),
            'invest_step': ('django.db.models.fields.FloatField', [], {}),
            'invest_target': ('django.db.models.fields.TextField', [], {}),
            'invest_threshold': ('django.db.models.fields.FloatField', [], {}),
            'max_expected_profit_rate': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'period': ('django.db.models.fields.FloatField', [], {}),
            'principle_guaranteed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'product_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'profit_calculation': ('django.db.models.fields.TextField', [], {}),
            'profit_end_date': ('django.db.models.fields.DateField', [], {}),
            'profit_rate': ('django.db.models.fields.FloatField', [], {}),
            'profit_start_date': ('django.db.models.fields.DateField', [], {}),
            'profit_target': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'profit_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'region': ('django.db.models.fields.TextField', [], {}),
            'related_target': ('django.db.models.fields.TextField', [], {}),
            'risk_level': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sale_end_date': ('django.db.models.fields.DateField', [], {}),
            'sale_start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['wanglibao_bank_financing']