# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Fund.AIP_able'
        db.delete_column(u'wanglibao_fund_fund', 'AIP_able')

        # Deleting field 'Fund.sales_url'
        db.delete_column(u'wanglibao_fund_fund', 'sales_url')

        # Deleting field 'Fund.portfolio'
        db.delete_column(u'wanglibao_fund_fund', 'portfolio')

        # Deleting field 'Fund.bank_redeem_condition'
        db.delete_column(u'wanglibao_fund_fund', 'bank_redeem_condition')

        # Deleting field 'Fund.client_redeemable'
        db.delete_column(u'wanglibao_fund_fund', 'client_redeemable')

        # Deleting field 'Fund.pledgable'
        db.delete_column(u'wanglibao_fund_fund', 'pledgable')

        # Deleting field 'Fund.start_date'
        db.delete_column(u'wanglibao_fund_fund', 'start_date')

        # Deleting field 'Fund.buy_description'
        db.delete_column(u'wanglibao_fund_fund', 'buy_description')

        # Deleting field 'Fund.end_date'
        db.delete_column(u'wanglibao_fund_fund', 'end_date')

        # Deleting field 'Fund.invest_type'
        db.delete_column(u'wanglibao_fund_fund', 'invest_type')

        # Deleting field 'Fund.frontend_hosting_charge_rate'
        db.delete_column(u'wanglibao_fund_fund', 'frontend_hosting_charge_rate')

        # Deleting field 'Fund.profit_description'
        db.delete_column(u'wanglibao_fund_fund', 'profit_description')

        # Deleting field 'Fund.hosted_bank_description'
        db.delete_column(u'wanglibao_fund_fund', 'hosted_bank_description')

        # Deleting field 'Fund.invest_target'
        db.delete_column(u'wanglibao_fund_fund', 'invest_target')

        # Deleting field 'Fund.management_period'
        db.delete_column(u'wanglibao_fund_fund', 'management_period')

        # Deleting field 'Fund.management_threshold'
        db.delete_column(u'wanglibao_fund_fund', 'management_threshold')

        # Deleting field 'Fund.management_charge_rate'
        db.delete_column(u'wanglibao_fund_fund', 'management_charge_rate')

        # Deleting field 'Fund.bank_redeemable'
        db.delete_column(u'wanglibao_fund_fund', 'bank_redeemable')

        # Deleting field 'Fund.mode'
        db.delete_column(u'wanglibao_fund_fund', 'mode')

        # Deleting field 'Fund.client_redeem_description'
        db.delete_column(u'wanglibao_fund_fund', 'client_redeem_description')

        # Deleting field 'Fund.available_region'
        db.delete_column(u'wanglibao_fund_fund', 'available_region')

        # Deleting field 'Fund.currency'
        db.delete_column(u'wanglibao_fund_fund', 'currency')

        # Deleting field 'Fund.issuable'
        db.delete_column(u'wanglibao_fund_fund', 'issuable')

        # Deleting field 'Fund.rate_day'
        db.delete_column(u'wanglibao_fund_fund', 'rate_day')

        # Deleting field 'Fund.scale'
        db.delete_column(u'wanglibao_fund_fund', 'scale')

        # Deleting field 'Fund.hosted_bank'
        db.delete_column(u'wanglibao_fund_fund', 'hosted_bank')

        # Deleting field 'Fund.profit_rate_7days'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_7days')

        # Deleting field 'Fund.risk_description'
        db.delete_column(u'wanglibao_fund_fund', 'risk_description')

        # Deleting field 'Fund.profit_per_month'
        db.delete_column(u'wanglibao_fund_fund', 'profit_per_month')

        # Deleting field 'Fund.redeemable'
        db.delete_column(u'wanglibao_fund_fund', 'redeemable')

        # Deleting field 'Fund.invest_step'
        db.delete_column(u'wanglibao_fund_fund', 'invest_step')

        # Deleting field 'Fund.profit_rate_3months'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_3months')

        # Deleting field 'Fund.target_user'
        db.delete_column(u'wanglibao_fund_fund', 'target_user')

        # Deleting field 'Fund.profit_rate_6months'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_6months')

        # Deleting field 'Fund.profit_rate_month'
        db.delete_column(u'wanglibao_fund_fund', 'profit_rate_month')

        # Deleting field 'Fund.invest_scope'
        db.delete_column(u'wanglibao_fund_fund', 'invest_scope')

        # Deleting field 'Fund.performance_compare_baseline'
        db.delete_column(u'wanglibao_fund_fund', 'performance_compare_baseline')

        # Adding field 'Fund.invest_risk'
        db.add_column(u'wanglibao_fund_fund', 'invest_risk',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.trade_status'
        db.add_column(u'wanglibao_fund_fund', 'trade_status',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'Fund.management_fee'
        db.add_column(u'wanglibao_fund_fund', 'management_fee',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.hosting_fee'
        db.add_column(u'wanglibao_fund_fund', 'hosting_fee',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.latest_shares'
        db.add_column(u'wanglibao_fund_fund', 'latest_shares',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.init_scale'
        db.add_column(u'wanglibao_fund_fund', 'init_scale',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.latest_scale'
        db.add_column(u'wanglibao_fund_fund', 'latest_scale',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.hosting_bank'
        db.add_column(u'wanglibao_fund_fund', 'hosting_bank',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'Fund.investment_target'
        db.add_column(u'wanglibao_fund_fund', 'investment_target',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.investment_scope'
        db.add_column(u'wanglibao_fund_fund', 'investment_scope',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.investment_strategy'
        db.add_column(u'wanglibao_fund_fund', 'investment_strategy',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.profit_allocation'
        db.add_column(u'wanglibao_fund_fund', 'profit_allocation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.risk_character'
        db.add_column(u'wanglibao_fund_fund', 'risk_character',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.rate_today'
        db.add_column(u'wanglibao_fund_fund', 'rate_today',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.rate_7_days'
        db.add_column(u'wanglibao_fund_fund', 'rate_7_days',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.rate_1_month'
        db.add_column(u'wanglibao_fund_fund', 'rate_1_month',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.rate_3_months'
        db.add_column(u'wanglibao_fund_fund', 'rate_3_months',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.rate_6_months'
        db.add_column(u'wanglibao_fund_fund', 'rate_6_months',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.rate_1_year'
        db.add_column(u'wanglibao_fund_fund', 'rate_1_year',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.profit_month'
        db.add_column(u'wanglibao_fund_fund', 'profit_month',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.added'
        db.add_column(u'wanglibao_fund_fund', 'added',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Fund.AIP_able'
        db.add_column(u'wanglibao_fund_fund', 'AIP_able',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Fund.sales_url'
        db.add_column(u'wanglibao_fund_fund', 'sales_url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Fund.portfolio'
        db.add_column(u'wanglibao_fund_fund', 'portfolio',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Fund.bank_redeem_condition'
        db.add_column(u'wanglibao_fund_fund', 'bank_redeem_condition',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.client_redeemable'
        db.add_column(u'wanglibao_fund_fund', 'client_redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fund.pledgable'
        db.add_column(u'wanglibao_fund_fund', 'pledgable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fund.start_date'
        db.add_column(u'wanglibao_fund_fund', 'start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fund.buy_description'
        db.add_column(u'wanglibao_fund_fund', 'buy_description',
                      self.gf('django.db.models.fields.TextField')(default=u'--'),
                      keep_default=False)

        # Adding field 'Fund.end_date'
        db.add_column(u'wanglibao_fund_fund', 'end_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fund.invest_type'
        db.add_column(u'wanglibao_fund_fund', 'invest_type',
                      self.gf('django.db.models.fields.CharField')(default=u'\u4fdd\u5b88\u578b', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.frontend_hosting_charge_rate'
        db.add_column(u'wanglibao_fund_fund', 'frontend_hosting_charge_rate',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.profit_description'
        db.add_column(u'wanglibao_fund_fund', 'profit_description',
                      self.gf('django.db.models.fields.TextField')(default=u'--'),
                      keep_default=False)

        # Adding field 'Fund.hosted_bank_description'
        db.add_column(u'wanglibao_fund_fund', 'hosted_bank_description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Fund.invest_target'
        db.add_column(u'wanglibao_fund_fund', 'invest_target',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Fund.management_period'
        db.add_column(u'wanglibao_fund_fund', 'management_period',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.management_threshold'
        db.add_column(u'wanglibao_fund_fund', 'management_threshold',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.management_charge_rate'
        db.add_column(u'wanglibao_fund_fund', 'management_charge_rate',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.bank_redeemable'
        db.add_column(u'wanglibao_fund_fund', 'bank_redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fund.mode'
        db.add_column(u'wanglibao_fund_fund', 'mode',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16),
                      keep_default=False)

        # Adding field 'Fund.client_redeem_description'
        db.add_column(u'wanglibao_fund_fund', 'client_redeem_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.available_region'
        db.add_column(u'wanglibao_fund_fund', 'available_region',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.currency'
        db.add_column(u'wanglibao_fund_fund', 'currency',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.issuable'
        db.add_column(u'wanglibao_fund_fund', 'issuable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Fund.rate_day'
        db.add_column(u'wanglibao_fund_fund', 'rate_day',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.scale'
        db.add_column(u'wanglibao_fund_fund', 'scale',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.hosted_bank'
        db.add_column(u'wanglibao_fund_fund', 'hosted_bank',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64),
                      keep_default=False)

        # Adding field 'Fund.profit_rate_7days'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_7days',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.risk_description'
        db.add_column(u'wanglibao_fund_fund', 'risk_description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Fund.profit_per_month'
        db.add_column(u'wanglibao_fund_fund', 'profit_per_month',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.redeemable'
        db.add_column(u'wanglibao_fund_fund', 'redeemable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Fund.invest_step'
        db.add_column(u'wanglibao_fund_fund', 'invest_step',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.profit_rate_3months'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_3months',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.target_user'
        db.add_column(u'wanglibao_fund_fund', 'target_user',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'Fund.profit_rate_6months'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_6months',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.profit_rate_month'
        db.add_column(u'wanglibao_fund_fund', 'profit_rate_month',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Fund.invest_scope'
        db.add_column(u'wanglibao_fund_fund', 'invest_scope',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Fund.performance_compare_baseline'
        db.add_column(u'wanglibao_fund_fund', 'performance_compare_baseline',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Deleting field 'Fund.invest_risk'
        db.delete_column(u'wanglibao_fund_fund', 'invest_risk')

        # Deleting field 'Fund.trade_status'
        db.delete_column(u'wanglibao_fund_fund', 'trade_status')

        # Deleting field 'Fund.management_fee'
        db.delete_column(u'wanglibao_fund_fund', 'management_fee')

        # Deleting field 'Fund.hosting_fee'
        db.delete_column(u'wanglibao_fund_fund', 'hosting_fee')

        # Deleting field 'Fund.latest_shares'
        db.delete_column(u'wanglibao_fund_fund', 'latest_shares')

        # Deleting field 'Fund.init_scale'
        db.delete_column(u'wanglibao_fund_fund', 'init_scale')

        # Deleting field 'Fund.latest_scale'
        db.delete_column(u'wanglibao_fund_fund', 'latest_scale')

        # Deleting field 'Fund.hosting_bank'
        db.delete_column(u'wanglibao_fund_fund', 'hosting_bank')

        # Deleting field 'Fund.investment_target'
        db.delete_column(u'wanglibao_fund_fund', 'investment_target')

        # Deleting field 'Fund.investment_scope'
        db.delete_column(u'wanglibao_fund_fund', 'investment_scope')

        # Deleting field 'Fund.investment_strategy'
        db.delete_column(u'wanglibao_fund_fund', 'investment_strategy')

        # Deleting field 'Fund.profit_allocation'
        db.delete_column(u'wanglibao_fund_fund', 'profit_allocation')

        # Deleting field 'Fund.risk_character'
        db.delete_column(u'wanglibao_fund_fund', 'risk_character')

        # Deleting field 'Fund.rate_today'
        db.delete_column(u'wanglibao_fund_fund', 'rate_today')

        # Deleting field 'Fund.rate_7_days'
        db.delete_column(u'wanglibao_fund_fund', 'rate_7_days')

        # Deleting field 'Fund.rate_1_month'
        db.delete_column(u'wanglibao_fund_fund', 'rate_1_month')

        # Deleting field 'Fund.rate_3_months'
        db.delete_column(u'wanglibao_fund_fund', 'rate_3_months')

        # Deleting field 'Fund.rate_6_months'
        db.delete_column(u'wanglibao_fund_fund', 'rate_6_months')

        # Deleting field 'Fund.rate_1_year'
        db.delete_column(u'wanglibao_fund_fund', 'rate_1_year')

        # Deleting field 'Fund.profit_month'
        db.delete_column(u'wanglibao_fund_fund', 'profit_month')

        # Deleting field 'Fund.added'
        db.delete_column(u'wanglibao_fund_fund', 'added')


    models = {
        u'wanglibao_fund.fund': {
            'Meta': {'object_name': 'Fund'},
            'accumulated_face_value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'brief': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'earned_per_10k': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'face_value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'found_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'hosting_bank': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'hosting_fee': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'init_scale': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'invest_risk': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'investment_scope': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'investment_strategy': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'investment_target': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wanglibao_fund.FundIssuer']"}),
            'latest_scale': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'latest_shares': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'management_fee': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'manager': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'profit_allocation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'profit_month': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_1_month': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_1_year': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_3_months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_6_months': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_7_days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'rate_today': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'risk_character': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'trade_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
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
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        },
        u'wanglibao_fund.issuefrontendchargerate': {
            'Meta': {'object_name': 'IssueFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        },
        u'wanglibao_fund.redeembackendchargerate': {
            'Meta': {'object_name': 'RedeemBackEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_back_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        },
        u'wanglibao_fund.redeemfrontendchargerate': {
            'Meta': {'object_name': 'RedeemFrontEndChargeRate'},
            'bottom_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'fund': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redeem_front_end_charge_rates'", 'to': u"orm['wanglibao_fund.Fund']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'top_line': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'percent'", 'max_length': '8'})
        }
    }

    complete_apps = ['wanglibao_fund']