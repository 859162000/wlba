# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'BankFinancing.face_value'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'face_value')

        # Deleting field 'BankFinancing.profit_target'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'profit_target')

        # Deleting field 'BankFinancing.profit_rate'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'profit_rate')

        # Deleting field 'BankFinancing.product_code'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'product_code')

        # Deleting field 'BankFinancing.invest_method'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'invest_method')

        # Deleting field 'BankFinancing.sale_end_date'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'sale_end_date')

        # Deleting field 'BankFinancing.invest_step'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'invest_step')

        # Deleting field 'BankFinancing.invest_threshold'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'invest_threshold')

        # Deleting field 'BankFinancing.profit_calculation'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'profit_calculation')

        # Deleting field 'BankFinancing.invest_target'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'invest_target')

        # Deleting field 'BankFinancing.product_type'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'product_type')

        # Deleting field 'BankFinancing.related_target'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'related_target')

        # Deleting field 'BankFinancing.sale_start_date'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'sale_start_date')

        # Adding field 'BankFinancing.expected_rate'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'expected_rate',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.issue_target'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'issue_target',
                      self.gf('django.db.models.fields.CharField')(default=u'\u4e2a\u4eba', max_length=16),
                      keep_default=False)

        # Adding field 'BankFinancing.investment_type'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'investment_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.issue_start_date'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'issue_start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.issue_end_date'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'issue_end_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.investment_threshold'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'investment_threshold',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.investment_step'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'investment_step',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.pledgable'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'pledgable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'BankFinancing.bank_pre_redeemable'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'bank_pre_redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'BankFinancing.client_redeemable'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'client_redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'BankFinancing.max_profit_rate'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'max_profit_rate',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.rate_compare_to_saving'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'rate_compare_to_saving',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.liquidity_level'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'liquidity_level',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.profit_description'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'profit_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.buy_description'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'buy_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.bank_pre_redeem_description'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'bank_pre_redeem_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.redeem_description'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'redeem_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.risk_description'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'risk_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'BankFinancing.added'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'added',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


        # Changing field 'BankFinancing.profit_start_date'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'profit_start_date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'BankFinancing.risk_level'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'risk_level', self.gf('django.db.models.fields.CharField')(max_length=16))

        # Changing field 'BankFinancing.profit_end_date'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'profit_end_date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'BankFinancing.period'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'period', self.gf('django.db.models.fields.IntegerField')())

    def backwards(self, orm):
        # Adding field 'BankFinancing.face_value'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'face_value',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.profit_target'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'profit_target',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32),
                      keep_default=False)

        # Adding field 'BankFinancing.profit_rate'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'profit_rate',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.product_code'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'product_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128),
                      keep_default=False)

        # Adding field 'BankFinancing.invest_method'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'invest_method',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'BankFinancing.sale_end_date'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'sale_end_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 3, 21, 0, 0)),
                      keep_default=False)

        # Adding field 'BankFinancing.invest_step'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'invest_step',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.invest_threshold'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'invest_threshold',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BankFinancing.profit_calculation'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'profit_calculation',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'BankFinancing.invest_target'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'invest_target',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'BankFinancing.product_type'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'product_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32),
                      keep_default=False)

        # Adding field 'BankFinancing.related_target'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'related_target',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'BankFinancing.sale_start_date'
        db.add_column(u'wanglibao_bank_financing_bankfinancing', 'sale_start_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 3, 21, 0, 0)),
                      keep_default=False)

        # Deleting field 'BankFinancing.expected_rate'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'expected_rate')

        # Deleting field 'BankFinancing.issue_target'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'issue_target')

        # Deleting field 'BankFinancing.investment_type'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'investment_type')

        # Deleting field 'BankFinancing.issue_start_date'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'issue_start_date')

        # Deleting field 'BankFinancing.issue_end_date'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'issue_end_date')

        # Deleting field 'BankFinancing.investment_threshold'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'investment_threshold')

        # Deleting field 'BankFinancing.investment_step'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'investment_step')

        # Deleting field 'BankFinancing.pledgable'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'pledgable')

        # Deleting field 'BankFinancing.bank_pre_redeemable'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'bank_pre_redeemable')

        # Deleting field 'BankFinancing.client_redeemable'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'client_redeemable')

        # Deleting field 'BankFinancing.max_profit_rate'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'max_profit_rate')

        # Deleting field 'BankFinancing.rate_compare_to_saving'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'rate_compare_to_saving')

        # Deleting field 'BankFinancing.liquidity_level'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'liquidity_level')

        # Deleting field 'BankFinancing.profit_description'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'profit_description')

        # Deleting field 'BankFinancing.buy_description'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'buy_description')

        # Deleting field 'BankFinancing.bank_pre_redeem_description'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'bank_pre_redeem_description')

        # Deleting field 'BankFinancing.redeem_description'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'redeem_description')

        # Deleting field 'BankFinancing.risk_description'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'risk_description')

        # Deleting field 'BankFinancing.added'
        db.delete_column(u'wanglibao_bank_financing_bankfinancing', 'added')


        # Changing field 'BankFinancing.profit_start_date'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'profit_start_date', self.gf('django.db.models.fields.DateField')(default=None))

        # Changing field 'BankFinancing.risk_level'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'risk_level', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'BankFinancing.profit_end_date'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'profit_end_date', self.gf('django.db.models.fields.DateField')(default=None))

        # Changing field 'BankFinancing.period'
        db.alter_column(u'wanglibao_bank_financing_bankfinancing', 'period', self.gf('django.db.models.fields.FloatField')())

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
            'status': ('django.db.models.fields.CharField', [], {'default': "u'\\u5728\\u552e'", 'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_bank_financing']