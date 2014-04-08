# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BankFinancing.short_name'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'short_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BankFinancing.short_name'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'short_name')


    models = {
        u'wanglibao_bank_financing.bank': {
            'Meta': {'object_name': 'Bank'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'wanglibao_bank_financing.bankfinancing': {
            'Meta': {'object_name': 'BankFinancing'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'bank': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_bank_financing.Bank']"}),
            'bank_pre_redeem_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bank_pre_redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'buy_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'client_redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "u'\\u4eba\\u6c11\\u5e01'", 'max_length': '32'}),
            'expected_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_step': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'investment_threshold': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'investment_type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'issue_end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'issue_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'issue_target': ('django.db.models.fields.CharField', [], {'default': "u'\\u4e2a\\u4eba'", 'max_length': '16'}),
            'liquidity_level': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'max_expected_profit_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'max_profit_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pledgable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'principle_guaranteed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profit_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profit_end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'profit_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'profit_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'rate_compare_to_saving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'redeem_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'region': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'risk_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'risk_level': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5728\\u552e'", 'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_bank_financing']