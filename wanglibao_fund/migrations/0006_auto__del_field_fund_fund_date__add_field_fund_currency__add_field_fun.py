# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Fund.fund_date'
        db.delete_column(u'wanglibao_fund_fund', 'fund_date')

        # Adding field 'Fund.currency'
        db.add_column(u'wanglibao_fund_fund', 'currency',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.target_user'
        db.add_column(u'wanglibao_fund_fund', 'target_user',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.available_region'
        db.add_column(u'wanglibao_fund_fund', 'available_region',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.invest_type'
        db.add_column(u'wanglibao_fund_fund', 'invest_type',
                      self.gf('django.db.models.fields.CharField')(default=u'\u4fdd\u5b88\u578b', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.profit_description'
        db.add_column(u'wanglibao_fund_fund', 'profit_description',
                      self.gf('django.db.models.fields.TextField')(default=u'--'),
                      keep_default=False)

        # Adding field 'Fund.buy_description'
        db.add_column(u'wanglibao_fund_fund', 'buy_description',
                      self.gf('django.db.models.fields.TextField')(default=u'--'),
                      keep_default=False)

        # Adding field 'Fund.found_date'
        db.add_column(u'wanglibao_fund_fund', 'found_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fund.start_date'
        db.add_column(u'wanglibao_fund_fund', 'start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fund.end_date'
        db.add_column(u'wanglibao_fund_fund', 'end_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fund.management_period'
        db.add_column(u'wanglibao_fund_fund', 'management_period',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.management_threshold'
        db.add_column(u'wanglibao_fund_fund', 'management_threshold',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.invest_step'
        db.add_column(u'wanglibao_fund_fund', 'invest_step',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.pledgable'
        db.add_column(u'wanglibao_fund_fund', 'pledgable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fund.bank_redeemable'
        db.add_column(u'wanglibao_fund_fund', 'bank_redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fund.bank_redeem_condition'
        db.add_column(u'wanglibao_fund_fund', 'bank_redeem_condition',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.client_redeemable'
        db.add_column(u'wanglibao_fund_fund', 'client_redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fund.client_redeem_description'
        db.add_column(u'wanglibao_fund_fund', 'client_redeem_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.risk_description'
        db.add_column(u'wanglibao_fund_fund', 'risk_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Fund.fund_date'
        db.add_column(u'wanglibao_fund_fund', 'fund_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 3, 20, 0, 0)),
                      keep_default=False)

        # Deleting field 'Fund.currency'
        db.delete_column(u'wanglibao_fund_fund', 'currency')

        # Deleting field 'Fund.target_user'
        db.delete_column(u'wanglibao_fund_fund', 'target_user')

        # Deleting field 'Fund.available_region'
        db.delete_column(u'wanglibao_fund_fund', 'available_region')

        # Deleting field 'Fund.invest_type'
        db.delete_column(u'wanglibao_fund_fund', 'invest_type')

        # Deleting field 'Fund.profit_description'
        db.delete_column(u'wanglibao_fund_fund', 'profit_description')

        # Deleting field 'Fund.buy_description'
        db.delete_column(u'wanglibao_fund_fund', 'buy_description')

        # Deleting field 'Fund.found_date'
        db.delete_column(u'wanglibao_fund_fund', 'found_date')

        # Deleting field 'Fund.start_date'
        db.delete_column(u'wanglibao_fund_fund', 'start_date')

        # Deleting field 'Fund.end_date'
        db.delete_column(u'wanglibao_fund_fund', 'end_date')

        # Deleting field 'Fund.management_period'
        db.delete_column(u'wanglibao_fund_fund', 'management_period')

        # Deleting field 'Fund.management_threshold'
        db.delete_column(u'wanglibao_fund_fund', 'management_threshold')

        # Deleting field 'Fund.invest_step'
        db.delete_column(u'wanglibao_fund_fund', 'invest_step')

        # Deleting field 'Fund.pledgable'
        db.delete_column(u'wanglibao_fund_fund', 'pledgable')

        # Deleting field 'Fund.bank_redeemable'
        db.delete_column(u'wanglibao_fund_fund', 'bank_redeemable')

        # Deleting field 'Fund.bank_redeem_condition'
        db.delete_column(u'wanglibao_fund_fund', 'bank_redeem_condition')

        # Deleting field 'Fund.client_redeemable'
        db.delete_column(u'wanglibao_fund_fund', 'client_redeemable')

        # Deleting field 'Fund.client_redeem_description'
        db.delete_column(u'wanglibao_fund_fund', 'client_redeem_description')

        # Deleting field 'Fund.risk_description'
        db.delete_column(u'wanglibao_fund_fund', 'risk_description')


    models = {
        u'wanglibao_fund.fund': {
            'AIP_able': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'Meta': {'object_name': 'Fund'},
            'accumulated_face_value': ('django.db.models.fields.FloatField', [], {}),
            'available_region': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bank_redeem_condition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bank_redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brief': ('django.db.models.fields.TextField', [], {}),
            'buy_description': ('django.db.models.fields.TextField', [], {'default': "u'--'"}),
            'client_redeem_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'client_redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'earned_per_10k': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'face_value': ('django.db.models.fields.FloatField', [], {}),
            'found_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'frontend_hosting_charge_rate': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hosted_bank': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hosted_bank_description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invest_scope': ('django.db.models.fields.TextField', [], {}),
            'invest_step': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'invest_target': ('django.db.models.fields.TextField', [], {}),
            'invest_type': ('django.db.models.fields.CharField', [], {'default': "u'\\u4fdd\\u5b88\\u578b'", 'max_length': '16', 'blank': 'True'}),
            'issuable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.FundIssuer']"}),
            'management_charge_rate': ('django.db.models.fields.FloatField', [], {}),
            'management_period': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'management_threshold': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'manager': ('django.db.models.fields.TextField', [], {}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'performance_compare_baseline': ('django.db.models.fields.TextField', [], {}),
            'pledgable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'portfolio': ('django.db.models.fields.TextField', [], {}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'profit_description': ('django.db.models.fields.TextField', [], {'default': "u'--'"}),
            'profit_per_month': ('django.db.models.fields.FloatField', [], {}),
            'profit_rate_3months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_rate_6months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_rate_7days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'profit_rate_month': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_day': ('django.db.models.fields.FloatField', [], {}),
            'redeemable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'risk_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sales_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'scale': ('django.db.models.fields.FloatField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'target_user': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'wanglibao_fund.fundissuer': {
            'Meta': {'object_name': 'FundIssuer'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'home_page': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'wanglibao_fund.issuebackendchargerate': {
            'Meta': {'object_name': 'IssueBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.issuefrontendchargerate': {
            'Meta': {'object_name': 'IssueFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.redeembackendchargerate': {
            'Meta': {'object_name': 'RedeemBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'wanglibao_fund.redeemfrontendchargerate': {
            'Meta': {'object_name': 'RedeemFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_fund']